"""Behavior checks with fictitious data; no mail, network or personal records."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('report', ROOT / 'skills/claim-atlas/scripts/render_report.py')
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)
spec = importlib.util.spec_from_file_location('audit', ROOT / 'tools/inspect_html.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'docs/demo-data.json').read_text(encoding='utf-8'))

    def test_demo_passes_audit_and_is_current(self):
        rendered = report.render(self.data)
        self.assertEqual(rendered, (ROOT / 'docs/demo-report.html').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'report.html'; path.write_text(rendered, encoding='utf-8')
            self.assertEqual(audit.audit(path), [])

    def test_hostile_mail_is_escaped(self):
        self.data['cases'][1]['title'] = '<img src=x onerror=alert(1)>'
        self.data['cases'][1]['summary'] = '</style><script>bad()</script>'
        html = report.render(self.data)
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;img', html)

    def test_unsafe_urls_rejected(self):
        for url in ['javascript:alert(1)', 'http://example.com', 'https://user:secret@example.com', 'https://example.com/\nwrong']:
            with self.subTest(url=url):
                self.data['cases'][0]['sources'][0]['url'] = url
                with self.assertRaises(ValueError): report.render(self.data)

    def test_filing_gate_and_closed_date(self):
        for field, value in [('eligibility', 'possible'), ('official_url', ''), ('verified_on', ''), ('deadline', '2020-01-01')]:
            data = copy.deepcopy(self.data); data['cases'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError): report.render(data)

    def test_confirmed_cannot_hide_unknown_criteria(self):
        self.data['cases'][0]['criteria'][0]['state'] = 'unknown'
        with self.assertRaises(ValueError): report.render(self.data)
        self.data['cases'][0]['criteria'] = []
        with self.assertRaises(ValueError): report.render(self.data)

    def test_unselected_path_is_not_a_coverage_gap(self):
        self.data['coverage'] = [row for row in self.data['coverage'] if row['status'] != 'partial']
        html = report.render(self.data)
        self.assertNotIn('Coverage has gaps', html)
        self.assertIn('Outside this scan', html)
        self.assertIn('This report is read-only', html)
        self.assertNotIn('Eligibility: confirmed', html)

    def test_mixed_history_does_not_claim_no_new_scan(self):
        self.data['coverage'] = [
            {'source':'Old report','status':'historical','detail':'Prior findings retained'},
            {'source':'New scan','status':'complete','detail':'Selected scope completed'}]
        self.assertIn('Includes prior research', report.render(self.data))
        self.assertNotIn('Prior research / no new scan', report.render(self.data))

    def test_zero_results_explain_the_outcome(self):
        self.data['cases'] = []
        self.assertIn('No matches identified yet; this scan has gaps.',report.render(self.data))
        self.data['coverage'] = [{'source':'Notice scan','status':'complete','detail':'Selected scope completed'}]
        self.assertIn('No matches found in the checked scope.',report.render(self.data))

    def test_duplicate_owner_rejected(self):
        self.data['cases'].append(copy.deepcopy(self.data['cases'][0]))
        with self.assertRaises(ValueError): report.render(self.data)

    def test_followup_references_tracked_owner(self):
        self.data['cases'][0].update(case_ref='demo-bright', eligibility='unknown')
        self.assertIn('View tracked claim', report.render(self.data))
        self.data['cases'][0]['case_ref'] = 'missing'
        with self.assertRaises(ValueError): report.render(self.data)

    def test_security_links_and_expired_credentials_rejected(self):
        for index, field, value in [(-1, 'sources', [{'label':'bad', 'url':'https://example.com'}]), (-2, 'details', [{'label':'Claim ID', 'value':'private'}])]:
            data = copy.deepcopy(self.data); data['cases'][index][field] = value
            with self.assertRaises(ValueError): report.render(data)

    def test_empty_report_keeps_lifecycle_and_discloses_coverage(self):
        self.data['cases'] = []
        html = report.render(self.data)
        for lane in [*report.LANES, 'payments']:
            self.assertIn(f'id="{lane}"', html)
        self.assertIn('Coverage has gaps', html)

    def test_counts_and_paid_subset(self):
        html = report.render(self.data)
        self.assertIn('<span>Filed &amp; tracking</span><b>02</b>', html)
        self.assertNotIn('href="#payments"', html)

    def test_atomic_write_preserves_input_on_render_error(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'out.html'; path.write_text('old', encoding='utf-8')
            self.data['cases'][0]['eligibility'] = 'unknown'
            with self.assertRaises(ValueError): report.atomic_write(path, report.render(self.data))
            self.assertEqual(path.read_text(), 'old')


if __name__ == '__main__': unittest.main()
