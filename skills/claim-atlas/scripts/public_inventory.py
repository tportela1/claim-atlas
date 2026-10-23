#!/usr/bin/env python3
"""Validate public-only discovery inventories and build repeatable search plans.

No network calls, mailbox access, or personal evidence storage. Run --help.
"""
import argparse
from datetime import date, timedelta
import json
from pathlib import Path
from urllib.parse import urlsplit


STATUSES = {'open', 'automatic', 'pending', 'closed', 'unverified'}


def iso(value):
    return date.fromisoformat(value)


def https(value):
    u = urlsplit(value)
    if u.scheme != 'https' or not u.hostname or u.username or u.password:
        raise ValueError('Expected a public HTTPS URL without credentials')


def fields(obj, required, optional=()):
    if not isinstance(obj, dict) or set(obj) - set(required) - set(optional) or set(required) - set(obj):
        raise ValueError('Missing or unexpected inventory fields')


def load(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    fields(data, ('version', 'as_of', 'sources', 'cases'))
    if data['version'] != 1:
        raise ValueError('Unsupported inventory version')
    today = iso(data['as_of'])
    if not isinstance(data['sources'], list) or not isinstance(data['cases'], list):
        raise ValueError('Sources and cases must be arrays')
    urls = set()
    for source in data['sources']:
        fields(source, ('url', 'coverage', 'pages'), ('limitation',))
        https(source['url'])
        if source['url'] in urls:
            raise ValueError('Duplicate source')
        urls.add(source['url'])
        if source['coverage'] not in ('complete', 'partial', 'blocked'):
            raise ValueError('Invalid coverage')
        if type(source['pages']) is not int or source['pages'] < 0:
            raise ValueError('Invalid page count')
        if source['coverage'] != 'complete' and not source.get('limitation'):
            raise ValueError('Partial or blocked sources require a limitation')
    keys = set()
    for case in data['cases']:
        fields(case, ('key', 'title', 'status', 'sources', 'search_terms'),
               ('official_url', 'verified_on', 'class_start', 'class_end', 'deadline'))
        if not isinstance(case['key'], str) or not case['key'].strip() or case['key'] in keys:
            raise ValueError('Missing or duplicate case identity')
        keys.add(case['key'])
        if case['status'] not in STATUSES or not isinstance(case['title'], str) or not case['title'].strip():
            raise ValueError('Invalid case status or title')
        if not isinstance(case['sources'], list) or not case['sources'] or not set(case['sources']) <= urls:
            raise ValueError('Cases must reference declared discovery sources')
        terms = case['search_terms']
        if not isinstance(terms, list) or not all(isinstance(t, str) and t.strip() and '"' not in t and '\n' not in t for t in terms):
            raise ValueError('Search terms must be public names without quotes or newlines')
        for field in ('class_start', 'class_end', 'deadline', 'verified_on'):
            if case.get(field):
                iso(case[field])
        if case.get('class_start') and case.get('class_end') and iso(case['class_start']) > iso(case['class_end']):
            raise ValueError('Reversed class period')
        if case.get('verified_on') and iso(case['verified_on']) > today:
            raise ValueError('Verification is later than inventory date')
        if case.get('official_url'):
            https(case['official_url'])
            # Multiple cases can share an administrator portal. Identity is the
            # normalized case key; URL equality alone cannot prove duplication.
        if case['status'] in ('open', 'automatic') and not (case.get('official_url') and case.get('verified_on')):
            raise ValueError('Actionable status needs official source and verification date')
        if case['status'] == 'open':
            if not terms or not case.get('deadline') or iso(case['deadline']) < today:
                raise ValueError('Open claim needs terms and a non-expired deadline')
    return data


def summarize(data):
    return {
        'as_of': data['as_of'],
        'coverage': 'complete' if data['sources'] and all(s['coverage'] == 'complete' for s in data['sources']) else 'partial',
        'sources': len(data['sources']),
        'unique_cases': len(data['cases']),
        'statuses': {s: sum(c['status'] == s for c in data['cases']) for s in sorted(STATUSES)},
        'note': 'Directory coverage only; this does not certify mailbox traversal or eligibility.',
    }


def plan(data):
    result = []
    for c in sorted(data['cases'], key=lambda c: c['key']):
        if c['status'] != 'open':
            continue
        start, end = c.get('class_start'), c.get('class_end')
        # These are local mailbox queries, never public web queries. Search each
        # alias separately on Outlook to avoid assuming provider OR semantics.
        gmail = 'in:anywhere {' + ' '.join('"' + t + '"' for t in c['search_terms']) + '}'
        if start:
            gmail += ' after:' + (iso(start) - timedelta(days=1)).strftime('%Y/%m/%d')
        if end:
            gmail += ' before:' + (iso(end) + timedelta(days=1)).strftime('%Y/%m/%d')
        outlook = []
        for term in c['search_terms']:
            q = '"' + term + '"'
            if start:
                q += ' received>=' + start
            if end:
                q += ' received<' + (iso(end) + timedelta(days=1)).isoformat()
            outlook.append(q)
        result.append({'key': c['key'], 'gmail': gmail, 'outlook': outlook,
                       'dates_complete': bool(start and end),
                       'follow_up': 'Page all results; adapt date boundaries to provider timezone; check event evidence and aliases. No hits leaves eligibility unknown.'})
    return result


def compare(previous, current):
    old = {c['key']: c for c in previous['cases']}
    now = {c['key']: c for c in current['cases']}
    return {'newly_discovered': sorted(now.keys() - old.keys()),
            'changed': sorted(k for k in now.keys() & old.keys() if any(now[k].get(f) != old[k].get(f) for f in ('status', 'deadline', 'class_start', 'class_end'))),
            'not_in_current_inventory': sorted(old.keys() - now.keys())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('validate', 'plan', 'compare'))
    parser.add_argument('inventory', help='Public-only inventory JSON; never supply email evidence')
    parser.add_argument('--previous', help='Previous public inventory, required for compare')
    args = parser.parse_args()
    try:
        data = load(args.inventory)
        if args.command == 'compare':
            if not args.previous:
                parser.error('compare requires --previous')
            result = compare(load(args.previous), data)
        else:
            result = plan(data) if args.command == 'plan' else summarize(data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.exit(1, f'Invalid public inventory: {exc}\n')


if __name__ == '__main__':
    main()
