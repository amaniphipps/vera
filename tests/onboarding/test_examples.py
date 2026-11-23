#!/usr/bin/env python3
"""Acceptance checks for Vera's centralized, rich synthetic examples."""
import csv
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
EXAMPLES = REPO / "skills/onboarding/meet-vera/examples"
PASSED = 0
FAILED = []


def check(name, condition):
    global PASSED
    if condition:
        PASSED += 1
        print(f"  PASS  {name}")
    else:
        FAILED.append(name)
        print(f"  FAIL  {name}")


def rows(name):
    with (EXAMPLES / "data" / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def main():
    manifest = json.loads((EXAMPLES / "data/manifest.json").read_text())
    arr = rows("arr-rollforward.csv")
    accounts = rows("crm-accounts.csv")
    opportunities = rows("crm-opportunities.csv")
    check("1,050 unique accounts", len(accounts) == len({r['account_id'] for r in accounts}) == 1050)
    check("1,050 ARR rows and 1,000 ending active", len(arr) == 1050 and sum(int(r['ending_arr']) > 0 for r in arr) == 1000)
    check("200 open and 400 closed opportunities", sum(bool(r['forecast_category']) for r in opportunities) == 200 and sum(not r['forecast_category'] for r in opportunities) == 400)
    check("12,578 linked records", manifest["total_linked_records"] == 12578)
    check("every ARR row reconciles", all(int(r['ending_arr']) == int(r['starting_arr']) + int(r['new_arr']) + int(r['expansion_arr']) - int(r['contraction_arr']) - int(r['churn_arr']) for r in arr))
    check("aggregate ARR matches manifest", sum(int(r['ending_arr']) for r in arr) == manifest['arr']['ending_arr'])
    check("open expected ARR matches manifest", sum(int(r['expected_arr_usd']) for r in opportunities if r['forecast_category']) == manifest['pipeline']['open_expected_arr_total'])
    check("only anonymized email domains", all(r['email'].endswith('@example.invalid') for r in rows('crm-contacts.csv')))

    voice = (EXAMPLES / "voice-examples.md").read_text()
    for heading in ["## 1. Social, banter, and team belonging", "## 2. Executive & analytical readout", "## 3. Multi-task parallel dispatch", "## 4. New capability / integration live", "## 5. Serious register"]:
        check(f"canonical voice register: {heading}", heading in voice)
    curator = (REPO / "skills/self-maintenance/voice-curator/SKILL.md").read_text()
    check("voice curator points to canonical examples", "skills/onboarding/meet-vera/examples/voice-examples.md" in curator or "../../onboarding/meet-vera/examples/voice-examples.md" in curator or "onboarding/meet-vera/examples/voice-examples.md" in curator)
    old_pointer = REPO / "skills/self-maintenance/voice-curator/references/voice-examples.md"
    check("old voice path remains a compatibility pointer", old_pointer.is_file() and "voice-examples.md" in old_pointer.read_text() and len(old_pointer.read_text()) < 1000)

    for rel in ["personas/vera.md", "skills/analysis/revops-analyst/SKILL.md"]:
        text = (REPO / rel).read_text()
        check(f"legacy credit-union figures removed from {rel}", "$17.1M" not in text and "$160K" not in text and "$58.6K" not in text)
    for rel in ["forecast.html", "funnel.html", "weekly-recap.html"]:
        text = (REPO / "skills/delivery/vera-reporting/templates" / rel).read_text()
        check(f"reporting template is neutral {rel}", all(value not in text for value in ["Northwind Trading", "Acme Logistics", "Dana Whitfield", "$2.1M", "2,400"]))

    result = subprocess.run([sys.executable, str(EXAMPLES / "scripts/validate_examples.py"), "--no-write"], capture_output=True, text=True)
    print(result.stdout, end="")
    if result.returncode:
        print(result.stderr, end="")
    check("generated example validation passes", result.returncode == 0)

    print(f"\n{PASSED} passed, {len(FAILED)} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
