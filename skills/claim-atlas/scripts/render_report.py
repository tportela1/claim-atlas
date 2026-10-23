#!/usr/bin/env python3
"""Render private Claim Atlas data as inert, offline HTML. Standard library only."""
import argparse
from collections import Counter
from datetime import date
from html import escape
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import urlsplit

LANES = {
    "next-steps": ("Next actions", "Review the rules and your supporting facts before deciding. Evidence support is not an administrator’s decision."),
    "discoveries": ("Matches to review", "Evidence can point to a match. Missing facts still need your review."),
    "verification": ("Verification needed", "Official rules or legitimacy need checking before proceeding."),
    "tracking": ("Filed & tracking", "Your submitted and automatically enrolled claims, including payments received."),
    "watchlist": ("Watchlist", "Relevant developments without an open filing action."),
    "closed": ("Closed windows", "Historical opportunities retained for context."),
    "safety": ("Security notes", "Questionable notices are kept separate from claim opportunities."),
}
MATCH_LABELS = {"confirmed": "Your facts: supported", "strong": "A specific match; facts missing", "possible": "Possible connection", "unknown": "More evidence needed", "not_eligible": "A requirement conflicts"}
STATES = {"supported", "unknown", "contradicted"}
ELIGIBILITY = {"confirmed", "strong", "possible", "unknown", "not_eligible"}
COVERAGE = {"complete", "partial", "blocked", "historical", "not_run"}


def safe_url(value):
    if not isinstance(value, str) or any(ord(c) < 33 for c in value):
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password
    except ValueError:
        return False


def iso(value):
    return date.fromisoformat(value)


def validate(data):
    if data.get("version") != 1:
        raise ValueError("Unsupported report version")
    iso(data["date"])
    for key in ("title", "mode"):
        if not isinstance(data.get(key), str):
            raise ValueError("Missing report text")
    if not isinstance(data.get("accounts"), list) or not all(isinstance(a, str) for a in data["accounts"]):
        raise ValueError("Accounts must be labels")
    if not isinstance(data.get("coverage"), list) or not data["coverage"]:
        raise ValueError("Coverage must be disclosed")
    for row in data["coverage"]:
        if row.get("status") not in COVERAGE or not all(isinstance(row.get(k), str) for k in ("source", "detail")):
            raise ValueError("Invalid coverage entry")
    if not isinstance(data.get("cases"), list):
        raise ValueError("Cases must be a list")
    keys = set()
    for case in data["cases"]:
        key = case.get("key")
        if not isinstance(key, str) or not key or key in keys:
            raise ValueError("Missing or duplicate case key")
        keys.add(key)
        if case.get("lane") not in {*LANES, "payments"}:
            raise ValueError("Invalid lifecycle lane")
        for field in ("title", "status", "summary", "next_step"):
            if not isinstance(case.get(field), str):
                raise ValueError("Missing case text")
        if case.get("eligibility", "unknown") not in ELIGIBILITY:
            raise ValueError("Invalid eligibility")
        for field in ("deadline", "verified_on"):
            if case.get(field):
                iso(case[field])
        for field in ("verification", "payout"):
            if field in case and not isinstance(case[field], str):
                raise ValueError("Invalid case text")
        if not all(isinstance(v, str) for v in case.get("evidence", [])):
            raise ValueError("Evidence must be text")
        for row in case.get("criteria", []):
            if row.get("state") not in STATES or not all(isinstance(row.get(k), str) for k in ("criterion", "detail")):
                raise ValueError("Invalid criterion")
        for row in case.get("details", []):
            if not all(isinstance(row.get(k), str) for k in ("label", "value")):
                raise ValueError("Invalid tracking detail")
            if case["lane"] == "closed" and any(w in row["label"].lower() for w in ("pin", "claim id")):
                raise ValueError("Expired cards must not contain private identifiers")
        for source in case.get("sources", []):
            if not safe_url(source.get("url")) or not isinstance(source.get("label"), str):
                raise ValueError("Source links must be HTTPS without credentials")
        if case["lane"] == "safety" and case.get("sources"):
            raise ValueError("Security cards must keep links inert")
        if case.get("eligibility") == "confirmed" and any(row["state"] != "supported" for row in case.get("criteria", [])):
            raise ValueError("Confirmed eligibility cannot contain unresolved or contradicted criteria")
        if case["lane"] == "next-steps" and not case.get("case_ref"):
            if not case.get("criteria"):
                raise ValueError("Filing actions need an explicit criterion check")
            if case.get("eligibility") != "confirmed" or not safe_url(case.get("official_url")) or not case.get("verified_on"):
                raise ValueError("Filing actions require verified rules and supported eligibility")
            if case.get("deadline") and iso(case["deadline"]) < iso(data["date"]):
                raise ValueError("Closed claims cannot be filing actions")
        if case.get("verified_on") and iso(case["verified_on"]) > iso(data["date"]):
            raise ValueError("Verification cannot be in the future")
    owners = {c["key"]: c for c in data["cases"]}
    for case in data["cases"]:
        if case.get("case_ref"):
            owner = owners.get(case["case_ref"])
            if case["lane"] != "next-steps" or not owner or owner["lane"] not in ("tracking", "payments"):
                raise ValueError("Follow-up must reference a tracked owner")
    return data


def e(value):
    return escape(str(value), quote=True)


def link(label, url):
    return f'<a href="{e(url)}" rel="noopener noreferrer">{e(label)} <span aria-hidden="true">↗</span></a>'


def deadline_label(value, as_of):
    day = iso(value)
    distance = (day - iso(as_of)).days
    when = f"{day:%b} {day.day}, {day.year}"
    if distance == 0: return when + " / due today"
    if distance > 0: return when + f" / in {distance} days"
    return when + " / window passed"


def render(data):
    validate(data)
    counts = Counter(c["lane"] for c in data["cases"])
    count = lambda lane: counts[lane] + (counts["payments"] if lane == "tracking" else 0)
    ids = {c["key"]: f'case-{i}' for i, c in enumerate(data["cases"])}
    def card(c):
        badges = f'<span class="badge">{e(c["status"])}</span>'
        if c.get("eligibility"):
            badges += f'<span class="badge neutral">{e(MATCH_LABELS[c["eligibility"]])}</span>'
        facts = ""
        for field, label in (("deadline", "Deadline"), ("payout", "Payment received" if c["lane"] == "payments" else "Estimated payment"), ("verification", "Official source check")):
            if c.get(field):
                value = deadline_label(c[field], data["date"]) if field == "deadline" else c[field]
                facts += f'<div><dt>{label}</dt><dd>{e(value)}</dd></div>'
        evidence = '<div class="evidence"><h4>What supports this</h4><ul>' + "".join(f'<li>{e(v)}</li>' for v in c.get("evidence", [])) + '</ul></div>' if c.get("evidence") else ''
        criteria = '<div class="criteria"><h4>Eligibility check</h4>' + "".join(f'<div class="criterion"><span class="state {e(r["state"])}">{e(r["state"])}</span><div><strong>{e(r["criterion"])}</strong><p>{e(r["detail"])}</p></div></div>' for r in c.get("criteria", [])) + '</div>' if c.get("criteria") else ''
        details = '<details><summary>Tracking details</summary><dl class="facts">' + "".join(f'<div><dt>{e(r["label"])}</dt><dd>{e(r["value"])}</dd></div>' for r in c.get("details", [])) + '</dl></details>' if c.get("details") else ''
        sources = ' · '.join(link(r["label"], r["url"]) for r in c.get("sources", []))
        official = link('Read official rules before deciding', c['official_url']) if c['lane'] == 'next-steps' and not c.get('case_ref') else ''
        owner = f' <a href="#{ids[c["case_ref"]]}">View tracked claim</a>' if c.get("case_ref") else ''
        return f'<article class="case-card" id="{ids[c["key"]]}"><div class="badges">{badges}</div><h3>{e(c["title"])}</h3><p class="case-summary">{e(c["summary"])}</p><dl class="facts">{facts}</dl>{evidence}{criteria}{details}<div class="next-step"><span>Next step</span><p>{e(c["next_step"])}{owner}</p></div><div class="official-action">{official}</div><div class="sources">{sources}</div></article>'
    nav = ''.join(f'<a href="#{lane}"><span>{e(label)}</span><b>{count(lane):02d}</b></a>' for lane, (label, _) in LANES.items() if count(lane))
    sections = ''
    for lane, (label, desc) in LANES.items():
        selected = sorted((c for c in data['cases'] if c['lane'] == lane), key=lambda c: (c.get('deadline') or '9999-12-31', c['title']))
        cards = ''.join(card(c) for c in selected)
        if lane == 'tracking':
            paid = ''.join(card(c) for c in data["cases"] if c["lane"] == 'payments')
            cards += f'<div id="payments" class="payments"><h3 class="subheading">Payments received <span>{counts["payments"]}</span></h3>{paid or "<p class=empty>No payments recorded yet.</p>"}</div>'
        elif not cards:
            cards = '<p class="empty">Nothing in this section for the reported scope.</p>'
        visibility = '' if count(lane) else ' hidden'
        sections += f'<section id="{lane}"{visibility}><div class="section-heading"><div><h2>{label}</h2><p>{desc}</p></div><span class="section-count">{count(lane):02d}</span></div>{cards}<a class="back-to-top" href="#top">Back to top ↑</a></section>'
    partial = any(r["status"] in {"partial", "blocked"} for r in data["coverage"])
    historical = any(r["status"] == "historical" for r in data["coverage"])
    scope_label = "Coverage has gaps" if partial else "Includes prior research" if historical and any(row["status"] == "complete" for row in data["coverage"]) else "Prior research / no new scan" if historical else "Selected scope checked"
    empty_outcome = '' if data['cases'] else '<p class="empty-outcome">' + ('No matches identified yet; this scan has gaps.' if partial else 'No matches found in the checked scope.') + '</p>'
    demo_note = '<p class="demo-note">Example report · All cases and evidence are fictitious.</p>' if data.get('demo') is True else ''
    default_summary = f"{counts['next-steps']} next {'step' if counts['next-steps'] == 1 else 'steps'} to review. {counts['discoveries']} potential {'match needs' if counts['discoveries'] == 1 else 'matches need'} a closer look."
    scope_tone = "partial" if partial else "historical" if historical else "complete"
    first_lane = next((lane for lane in LANES if count(lane)), "coverage")
    first_label = {"next-steps":"Review your next step", "discoveries":"Review potential matches", "verification":"Review verification questions"}.get(first_lane,"Open your research record")
    coverage = ''.join(f'<div class="coverage-row"><div><strong>{e(r["source"])}</strong><span class="state {e(r["status"])}">{e("Outside this scan" if r["status"] == "not_run" else r["status"].replace("_", " "))}</span></div><p>{e(r["detail"])}</p></div>' for r in data["coverage"])
    css = (Path(__file__).resolve().parents[1] / 'assets' / 'report.css').read_text(encoding='utf-8')
    mark = (Path(__file__).resolve().parents[1] / 'assets' / 'logo-mark.svg').read_text(encoding='utf-8')
    accounts = ', '.join(data['accounts']) or 'No mailbox searched'
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; base-uri 'none'; form-action 'none'"><title>{e(data['title'])} · Claim Atlas</title><style>{css}</style></head>
<body id="top"><a class="skip-link" href="#main">Skip to report</a><aside class="sidebar"><div class="brand">{mark}<span>Claim Atlas<small>Find your next step.</small></span></div><p class="nav-label">YOUR WORKSPACE</p><nav aria-label="Report sections">{nav}</nav><a class="coverage-link" href="#coverage">Scope &amp; sources ↓</a><p class="local-note">Private by default.<br>Nothing is submitted from this report.</p></aside><main id="main"><header class="hero">{demo_note}<p class="eyebrow">SETTLEMENT DISCOVERY / {e(data['date'])}</p><h1>{e(data['title'])}</h1><p class="lede">{e(data.get('summary', default_summary))}</p>{empty_outcome}<div class="overview"><div><strong>{counts['next-steps']}</strong><span>next steps</span></div><div><strong>{counts['discoveries']}</strong><span>matches to review</span></div><div><strong>{count('tracking')}</strong><span>tracked claims</span></div></div><a class="start-link" href="#{first_lane}">{first_label} ↓</a><p class="continuation">This report is read-only. Read the evidence below, then return to your assistant to answer a question or record progress.</p></header><div class="scope"><span class="scope-status {scope_tone}">{scope_label}</span><div><strong>{e(data['mode'])}</strong><p>{e(accounts)} · <a href="#coverage">See exactly what was checked</a></p></div></div>{sections}<section id="coverage"><div class="section-heading"><div><p class="eyebrow">THE RESEARCH RECORD</p><h2>Scope &amp; sources</h2><p>Coverage describes this run, not the entire web or every possible claim.</p></div></div>{coverage}</section><footer>Claim Atlas · A personal research workspace. Potential matches require truthful eligibility review.<br>Private report · Generated {e(data['date'])}</footer></main></body></html>'''


def atomic_write(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.report-', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(content)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.data.resolve() == args.output.resolve():
        parser.error('Input and output must differ')
    try:
        atomic_write(args.output, render(json.loads(args.data.read_text(encoding='utf-8-sig'))))
    except (ValueError, KeyError, TypeError, OSError):
        parser.exit(1, 'Report was not written: invalid data or inaccessible files.\n')
    print('Report rendered. No mail accessed or tracking state changed.')


if __name__ == '__main__':
    main()
