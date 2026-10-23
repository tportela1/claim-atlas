import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('records',ROOT/'skills/claim-atlas/scripts/records.py')
records=importlib.util.module_from_spec(spec);spec.loader.exec_module(records)

class Records(unittest.TestCase):
    def test_filing_and_payment_are_distinct_and_repeat_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'claims.json'
            records.append(path,'case-a','Example','filed','2026-10-01')
            records.append(path,'case-a','Example','paid','2026-10-23','24')
            data=records.append(path,'case-a','Example','paid','2026-10-23','24.00')
            self.assertEqual(len(data['claims']['case-a']['events']),2)
            self.assertEqual(data['claims']['case-a']['status'],'paid')
            self.assertEqual(data['claims']['case-a']['events'][-1]['amount'],'24.00')
            self.assertTrue(path.with_suffix('.json.bak').exists())
    def test_corrupt_store_and_invalid_amount_do_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'claims.json';path.write_text('not json')
            with self.assertRaises(ValueError):records.append(path,'a','A','filed','2026-10-23')
            self.assertEqual(path.read_text(),'not json')
            for amount in ['-1','NaN','2.001',None]:
                with self.subTest(amount=amount),self.assertRaises(ValueError):records.append(path,'a','A','paid','2026-10-23',amount)
    def test_unrecognized_fields_survive(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'claims.json';path.write_text(json.dumps({'version':1,'custom':True,'claims':{}}))
            result=records.append(path,'a','A','dismissed','2026-10-23')
            self.assertTrue(result['custom'])
