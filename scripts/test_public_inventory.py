"""Offline tests using fictitious public cases; no real mailbox access."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import sys

MODULE = Path(__file__).resolve().parents[1] / 'skills/claim-atlas/scripts/public_inventory.py'
spec = importlib.util.spec_from_file_location('inventory', MODULE)
inventory = importlib.util.module_from_spec(spec)
sys.dont_write_bytecode = True
spec.loader.exec_module(inventory)


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.data = {'version': 1, 'as_of': '2026-10-22',
                     'sources': [{'url': 'https://example.org/list', 'coverage': 'complete', 'pages': 2}],
                     'cases': [{'key': 'example-2026', 'title': 'Example Widgets', 'status': 'open',
                                'sources': ['https://example.org/list'], 'search_terms': ['Example Widgets', 'Former Brand'],
                                'official_url': 'https://example.org/case', 'verified_on': '2026-10-22',
                                'deadline': '2026-12-01', 'class_start': '2017-01-01', 'class_end': '2024-12-31'}]}

    def load(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / 'public.json'
            p.write_text(json.dumps(self.data), encoding='utf-8')
            return inventory.load(p)

    def test_plan_uses_full_class_period_without_notice_filter(self):
        row = inventory.plan(self.load())[0]
        self.assertIn('after:2016/12/31', row['gmail'])
        self.assertIn('before:2025/01/01', row['gmail'])
        self.assertNotIn('subject:', row['gmail'])
        self.assertEqual(len(row['outlook']), 2)
        self.assertNotIn('eligibility', row)

    def test_pending_case_is_not_an_open_search_task(self):
        self.data['cases'][0]['status'] = 'pending'
        self.assertEqual(inventory.plan(self.load()), [])

    def test_partial_sources_cannot_claim_complete(self):
        self.data['sources'][0].update(coverage='blocked', limitation='Source unavailable')
        self.assertEqual(inventory.summarize(self.load())['coverage'], 'partial')

    def test_expired_open_claim_rejected(self):
        self.data['cases'][0]['deadline'] = '2025-01-01'
        with self.assertRaises(ValueError): self.load()

    def test_duplicate_case_rejected(self):
        duplicate = copy.deepcopy(self.data['cases'][0])
        self.data['cases'].append(duplicate)
        with self.assertRaises(ValueError): self.load()

    def test_different_cases_can_share_a_portal(self):
        other = copy.deepcopy(self.data['cases'][0])
        other['key'] = 'different-case-2026'
        self.data['cases'].append(other)
        self.assertEqual(len(self.load()['cases']), 2)

    def test_private_evidence_field_rejected(self):
        self.data['cases'][0]['email_body'] = 'Private content must not enter the public inventory'
        with self.assertRaises(ValueError): self.load()

    def test_open_case_needs_official_verification(self):
        del self.data['cases'][0]['official_url']
        with self.assertRaises(ValueError): self.load()

    def test_diff_separates_new_from_changed(self):
        old = self.load()
        self.data['cases'][0]['deadline'] = '2026-12-15'
        new = self.load()
        self.assertEqual(inventory.compare(old, new)['newly_discovered'], [])
        self.assertEqual(inventory.compare(old, new)['changed'], ['example-2026'])


if __name__ == '__main__': unittest.main()
