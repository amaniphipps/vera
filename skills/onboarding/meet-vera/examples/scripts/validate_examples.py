#!/usr/bin/env python3
"""Validate generated examples and record output hashes and honest QA scope."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
MANIFEST_PATH = DATA / "manifest.json"
M = json.loads(MANIFEST_PATH.read_text())

REQUIRED_HTML = [
    "index.html", "mock-arr-waterfall.html", "mock-briefing-email.html", "mock-forecast.html", "mock-slides.html",
    "mock-activation-funnel.html", "mock-weekly-recap.html",
    "tour/mock-revenue-dashboard.html", "tour/pipeline-motion.html", "tour/campaign-one-pager.html",
    "tour/win-loss-brief.html", "tour/pipeline-analysis.html", "tour/quota-commission.html", "tour/project-plan.html",
]
REQUIRED_OTHER = [
    "README.md", "mock-arr-rollforward.md", "mock-arr-rollforward.xlsx", "mock-pipeline.csv",
    "mock-weekly-briefing.md", "mock-briefing-slack.md", "mock-briefing-text.txt", "voice-examples.md",
    "onboarding-conversation.md", "pdf-examples.md", "data/data-dictionary.md", "data/office-validation.json",
    "documents/mock-revenue-review.docx", "documents/mock-pipeline-review.docx",
    "documents/mock-campaign-one-pager.docx", "documents/mock-project-plan.docx",
    "presentations/mock-revenue-review.pptx", "tour/index.md",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    checks = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})
        if not condition:
            print(f"FAIL  {name} {detail}")

    for name, expected in M["source_sha256"].items():
        path = BASE / name if name == "mock-pipeline.csv" else DATA / name
        check(f"source hash {name}", path.is_file() and sha256(path) == expected)

    for name in REQUIRED_HTML + REQUIRED_OTHER:
        check(f"exists {name}", (BASE / name).is_file() and (BASE / name).stat().st_size > 0)

    for name in REQUIRED_HTML:
        path = BASE / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        check(f"synthetic label {name}", "Synthetic" in text or "synthetic" in text)
        check(f"attribution {name}", "Built by Vera" in text)
        check(f"responsive viewport {name}", 'name="viewport"' in text)
        check(f"no legacy placeholders {name}", not re.search(r"Mock artifact:|Full interactive version lands|lorem ipsum|\bTBD\b|\bTODO\b", text, re.I))
        check(f"no em dash {name}", "—" not in text)
        check(f"no external scripts {name}", not re.search(r"<script[^>]+src=|<link[^>]+href=['\"]https?://|url\(['\"]?https?://", text, re.I))
        check(f"no remote image {name}", not re.search(r"<(?:img|image)[^>]+(?:src|href)=['\"]https?://", text, re.I))
    check("no new skill manifests", not list(BASE.rglob("SKILL.md")) and not list(BASE.rglob("skill.yaml")))

    with (BASE / "mock-pipeline.csv").open(newline="", encoding="utf-8") as handle:
        pipeline = list(csv.DictReader(handle))
    check("backwards pipeline has 200 rows", len(pipeline) == 200)

    if (BASE / "mock-arr-rollforward.xlsx").is_file():
        import openpyxl
        workbook_path = BASE / "mock-arr-rollforward.xlsx"
        check("xlsx valid zip", zipfile.is_zipfile(workbook_path))
        wb = openpyxl.load_workbook(workbook_path, data_only=False, read_only=False)
        check("xlsx required sheets", {"ARR Rollforward", "Open Pipeline", "Closed Opportunities", "Accounts", "Activation", "Validation"} <= set(wb.sheetnames), str(wb.sheetnames))
        check("xlsx has all ARR rows", wb["ARR Rollforward"].max_row >= 1051, str(wb["ARR Rollforward"].max_row))
        check("xlsx has all open rows", wb["Open Pipeline"].max_row >= 201, str(wb["Open Pipeline"].max_row))
        check("xlsx has all closed rows", wb["Closed Opportunities"].max_row >= 401, str(wb["Closed Opportunities"].max_row))
        formulas = [cell.value for ws in wb.worksheets for row in ws.iter_rows() for cell in row if cell.data_type == "f"]
        check("xlsx contains formulas", len(formulas) >= 10, str(len(formulas)))
        check("xlsx avoids unsupported formulas", not any(re.search(r"XLOOKUP|XMATCH|\bFILTER\(|\bSEQUENCE\(", f, re.I) for f in formulas))
        check("xlsx recalculates on load", bool(wb.calculation.fullCalcOnLoad and wb.calculation.forceFullCalc))
        wb.close()

    for name in [p for p in REQUIRED_OTHER if p.endswith(".docx") or p.endswith(".pptx")]:
        path = BASE / name
        if not path.is_file():
            continue
        check(f"office valid zip {name}", zipfile.is_zipfile(path))
        with zipfile.ZipFile(path) as package:
            check(f"office package content {name}", "[Content_Types].xml" in package.namelist())
            xml_text = "".join(package.read(n).decode("utf-8", errors="ignore") for n in package.namelist() if n.endswith(".xml"))
            check(f"office synthetic label {name}", "Synthetic" in xml_text or "synthetic" in xml_text)
            check(f"office attribution {name}", "Built by Vera" in xml_text)

    office_validation_path = DATA / "office-validation.json"
    if office_validation_path.is_file():
        office_validation = json.loads(office_validation_path.read_text())
        office_text = json.dumps(office_validation).lower()
        check("Office recalc/render limits disclosed", "not inspected" in office_text and "libreoffice" in office_text)

    summary = {
        "status": "PASS" if all(c["pass"] for c in checks) else "FAIL",
        "checks_passed": sum(c["pass"] for c in checks),
        "checks_failed": sum(not c["pass"] for c in checks),
        "checks": checks,
        "office_formula_recalculation": "not inspected - LibreOffice unavailable",
        "office_visual_rendering": "not inspected - LibreOffice unavailable",
    }
    if not args.no_write:
        summary["source_manifest_sha256"] = sha256(MANIFEST_PATH)
        summary["outputs"] = {name: sha256(BASE / name) for name in REQUIRED_HTML + REQUIRED_OTHER if (BASE / name).is_file()}
        (DATA / "validation-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ["status", "checks_passed", "checks_failed", "office_formula_recalculation", "office_visual_rendering"]}, indent=2))
    if summary["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
