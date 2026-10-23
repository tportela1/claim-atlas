#!/usr/bin/env python3
"""Append user-authorized claim events to Claim Atlas's local record."""
import argparse
from datetime import date
from decimal import Decimal, InvalidOperation
import json
import os
from pathlib import Path
import tempfile

EVENTS={'watched','filed','enrolled','paid','dismissed'}

def read(path):
    if not Path(path).exists(): return {'version':1,'claims':{}}
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    if data.get('version')!=1 or not isinstance(data.get('claims'),dict): raise ValueError('Unsupported record; original left unchanged')
    return data

def append(path,key,title,event,on,amount=None):
    date.fromisoformat(on)
    if not key.strip() or not title.strip() or event not in EVENTS: raise ValueError('Missing case identity or event')
    if event=='paid':
        try: value=Decimal(amount)
        except (InvalidOperation,TypeError): raise ValueError('Payment amount required') from None
        if not value.is_finite() or value<=0 or value.as_tuple().exponent < -2: raise ValueError('Use a positive amount with at most two decimals')
        amount=format(value,'.2f')
    elif amount is not None: raise ValueError('Only payment events accept an amount')
    path=Path(path);data=read(path)
    claim=data['claims'].setdefault(key,{'title':title,'events':[]})
    if not isinstance(claim.get('events'),list): raise ValueError('Invalid event history; original left unchanged')
    item={'kind':event,'on':on}
    if amount is not None:item.update(amount=amount,currency='USD')
    if item in claim['events']:return data
    claim['title']=title;claim['status']=event;claim['events'].append(item)
    payload=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,temporary=tempfile.mkstemp(prefix='.claims-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as stream:stream.write(payload)
        if path.exists():
            # Back up only successfully parsed input before publishing an update.
            backup=path.with_suffix(path.suffix+'.bak')
            backup.write_bytes(path.read_bytes())
        os.replace(temporary,path)
    finally:
        if os.path.exists(temporary):os.unlink(temporary)
    return data

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store',type=Path,default=Path.home()/'.claim-atlas/claims.json')
    parser.add_argument('--case',required=True);parser.add_argument('--title',required=True)
    parser.add_argument('--event',choices=sorted(EVENTS),required=True)
    parser.add_argument('--on',required=True);parser.add_argument('--amount')
    args=parser.parse_args()
    try:append(args.store,args.case,args.title,args.event,args.on,args.amount)
    except (ValueError,OSError):parser.exit(1,'Record not updated. Check the input and existing file.\n')
    print('Claim Atlas record updated. No claim was submitted.')

if __name__=='__main__':main()
