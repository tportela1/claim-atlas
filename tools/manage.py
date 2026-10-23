#!/usr/bin/env python3
"""Claim Atlas maintenance: install, build and verify using Python 3.10+."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'claim-atlas'

def sources():
    for path in sorted(SKILL.rglob('*'), key=lambda item: item.relative_to(SKILL).as_posix()):
        relative = path.relative_to(SKILL)
        if path.is_file() and not {'output','__pycache__'} & set(relative.parts) and path.suffix != '.pyc' and path.name != '.DS_Store':
            payload = path.read_bytes()
            if path.suffix in {'.md','.py','.json','.svg','.css','.yaml'} or path.name == 'LICENSE':
                payload = payload.replace(b'\r\n',b'\n')
            yield relative.as_posix(), payload

def write(path, content):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, staged = tempfile.mkstemp(dir=path.parent, prefix='.atlas-')
    try:
        with os.fdopen(descriptor,'wb') as stream: stream.write(content)
        os.replace(staged,path)
    finally:
        if os.path.exists(staged): os.unlink(staged)

def install(host, destination=None):
    home = Path.home()
    roots = {'codex':Path(os.environ.get('CODEX_HOME',home/'.codex'))/'skills', 'claude':home/'.claude/skills', 'agents':home/'.agents/skills'}
    parent = Path(destination) if destination else roots[host]
    target = parent/'claim-atlas'
    parent.mkdir(parents=True,exist_ok=True)
    if target.is_symlink(): raise ValueError('Choose a real install directory; the existing skill is a symlink')
    with tempfile.TemporaryDirectory(prefix='.atlas-install-',dir=parent) as work:
        staged = Path(work)/'skill'; staged.mkdir()
        for relative, payload in sources(): write(staged/relative,payload)
        previous = Path(work)/'previous'
        # Preserve old installer-managed output as an opaque user-owned tree.
        output = target/'output'
        if output.is_symlink():
            (staged/'output').symlink_to(os.readlink(output),target_is_directory=True)
        elif output.exists(): shutil.copytree(output,staged/'output')
        if target.exists(): target.rename(previous)
        try: staged.rename(target)
        except OSError:
            if previous.exists(): previous.rename(target)
            raise
    return target

def standalone():
    body = (SKILL/'SKILL.md').read_text(encoding='utf-8').rstrip()
    body += '\n\n> File edition: embedded guides below replace relative file references. Local utilities are optional; follow their documented contracts when execution is unavailable.\n'
    for relative, content in sources():
        if relative == 'SKILL.md': continue
        if relative.endswith('.md') or relative == 'LICENSE':
            body += '\n\n# Included guide: '+relative+'\n\n'+content.decode('utf-8').rstrip()+'\n'
        elif relative.endswith(('.py','.css','.svg','.json')):
            language = Path(relative).suffix[1:]
            body += '\n\n# Included resource: '+relative+'\n\n```'+language+'\n'+content.decode('utf-8').rstrip()+'\n```\n'
    return body.encode('utf-8')

def build(destination):
    destination = Path(destination); destination.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.atlas-build-',dir=destination) as work:
        archive = Path(work)/'claim-atlas.zip'
        with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_STORED) as output:
            for relative, payload in sources():
                entry = zipfile.ZipInfo('claim-atlas/'+relative,(2026,1,1,0,0,0))
                entry.create_system=3; entry.external_attr=0o100644<<16
                output.writestr(entry,payload)
        payload = archive.read_bytes()
        editions = {'claim-atlas.zip':payload,'claim-atlas.skill':payload,'claim-atlas-single-file.md':standalone()}
        # Each destination is atomically replaced; every edition is validated
        # before any release file is touched. A failed write remains detectable
        # by check(), rather than being presented as a successful release.
        with zipfile.ZipFile(archive) as check:
            if check.testzip(): raise ValueError('Archive validation failed')
        for filename, data in editions.items(): write(destination/filename,data)

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec); spec.loader.exec_module(result); return result

def check():
    subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests')],check=True)
    subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'scripts'),'-p','test_*.py'],check=True)
    expected={'claim-atlas/'+name:data for name,data in sources()}
    for suffix in ('zip','skill'):
        with zipfile.ZipFile(ROOT/'dist'/('claim-atlas.'+suffix)) as archive:
            if archive.testzip() or {n:archive.read(n) for n in archive.namelist()} != expected: raise ValueError('Release archive does not match skill source')
    if (ROOT/'dist/claim-atlas.zip').read_bytes() != (ROOT/'dist/claim-atlas.skill').read_bytes(): raise ValueError('Upload editions differ')
    if (ROOT/'dist/claim-atlas-single-file.md').read_bytes() != standalone(): raise ValueError('File edition is stale')
    report=module('atlas_report',SKILL/'scripts/render_report.py')
    fixture=json.loads((ROOT/'docs/demo-data.json').read_text(encoding='utf-8'))
    if report.render(fixture) != (ROOT/'docs/demo-report.html').read_text(encoding='utf-8'): raise ValueError('Demo is stale')
    print('Claim Atlas checks passed.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    command=parser.add_subparsers(dest='command',required=True)
    setup=command.add_parser('install'); setup.add_argument('--host',choices=['codex','claude','agents'],required=True); setup.add_argument('--destination',type=Path)
    release=command.add_parser('build'); release.add_argument('--output',type=Path,default=ROOT/'dist')
    command.add_parser('check')
    args=parser.parse_args()
    if args.command=='install': print('Installed Claim Atlas:',install(args.host,args.destination))
    elif args.command=='build': build(args.output); print('Built Claim Atlas editions.')
    else: check()

if __name__=='__main__': main()
