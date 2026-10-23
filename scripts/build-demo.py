#!/usr/bin/env python3
"""Build the public report from fictitious data only."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('report', ROOT / 'skills/claim-atlas/scripts/render_report.py')
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)
report.atomic_write(ROOT / 'docs/demo-report.html', report.render(json.loads((ROOT / 'docs/demo-data.json').read_text(encoding='utf-8'))))
print('Fictitious demo rebuilt.')
