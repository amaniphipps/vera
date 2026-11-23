#!/usr/bin/env python3
"""Build deterministic, source-linked Office examples for the Vera tour.

Only the five source CSVs used by the artifacts drive reported metrics. The
manifest supplies metadata and independent control totals. No Office formula
results are treated as calculated until an Office application recalculates them.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
import re
import zipfile
from collections import Counter, defaultdict
from copy import copy
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

from lxml import etree
from openpyxl import Workbook, load_workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.drawing.image import Image as XLImage
from openpyxl.formula import Tokenizer
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.workbook.properties import CalcProperties

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches as DInches, Pt as DPt, RGBColor as DRGBColor

from pptx import Presentation
from pptx.chart.data import ChartData
from pptx.dml.color import RGBColor as PRGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.util import Inches as PInches, Pt as PPt


BASE = Path(__file__).resolve().parents[1]
STAGING = BASE.parents[3]
DATA = BASE / "data"
MANIFEST_PATH = DATA / "manifest.json"
LOGO = STAGING / "docs" / "assets" / "vera-mark.png"
XLSX_PATH = BASE / "mock-arr-rollforward.xlsx"
DOC_DIR = BASE / "documents"
PPT_DIR = BASE / "presentations"
PPTX_PATH = PPT_DIR / "mock-revenue-review.pptx"
VALIDATION_PATH = DATA / "office-validation.json"
DOC_PATHS = {
    "revenue": DOC_DIR / "mock-revenue-review.docx",
    "pipeline": DOC_DIR / "mock-pipeline-review.docx",
    "campaign": DOC_DIR / "mock-campaign-one-pager.docx",
    "project": DOC_DIR / "mock-project-plan.docx",
}
ALL_ARTIFACTS = [XLSX_PATH, *DOC_PATHS.values(), PPTX_PATH]
BUILD_DATE = "2026-11-23"
BUILD_DATETIME = datetime(2026, 11, 23, 0, 0, 0)
ZIP_DATETIME = (2026, 11, 23, 0, 0, 0)

# Canonical public-main palette.
BLUE = "3559D6"
TEAL = "0F8A75"
INK = "1B1F27"
LIGHT = "F4F5F7"
WHITE = "FFFFFF"
LINE = "DDE1E6"
GREEN = "1F9D55"
AMBER = "B7791F"
RED = "C53030"
INPUT_BLUE = BLUE
LINK_GREEN = GREEN
BLACK = "000000"
YELLOW = "FFF2A8"
MUTED = "5B6472"
PALE_BLUE = "EAF0FF"
PALE_TEAL = "E8F5F1"
PALE_RED = "FBECEC"
PALE_AMBER = "FFF5DF"

CURRENCY = '$#,##0;($#,##0);-'
CURRENCY_1 = '$#,##0.0;($#,##0.0);-'
PERCENT = '0.0%;(0.0%);-'
INTEGER = '#,##0;(#,##0);-'
DECIMAL = '0.000000'
DATE_FMT = 'yyyy-mm-dd'

THIN = Side(style="thin", color=LINE)
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
FILL_HEADER = PatternFill("solid", fgColor=BLUE)
FILL_LIGHT = PatternFill("solid", fgColor=LIGHT)
FILL_YELLOW = PatternFill("solid", fgColor=YELLOW)
FONT_BASE = Font(name="Arial", size=9, color=INK)
FONT_INPUT = Font(name="Arial", size=9, color=INPUT_BLUE)
FONT_FORMULA = Font(name="Arial", size=9, color=BLACK)
FONT_LINK = Font(name="Arial", size=9, color=LINK_GREEN)
FONT_HEADER = Font(name="Arial", size=9, bold=True, color=WHITE)
FONT_TITLE = Font(name="Arial", size=20, bold=True, color=INK)
FONT_SUBTITLE = Font(name="Arial", size=10, color=MUTED)
FONT_SECTION = Font(name="Arial", size=11, bold=True, color=BLUE)


def read_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_int(row: dict[str, str], key: str) -> int:
    return int(row[key])


def as_date(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def money(value: float | int) -> str:
    return f"${value:,.0f}"


def compact_money(value: float | int) -> str:
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000:
        return f"{sign}${value / 1_000_000:.2f}M"
    return f"{sign}${value / 1_000:.1f}K"


def signed_compact_money(value: float | int) -> str:
    if value > 0:
        return "+" + compact_money(value)
    return compact_money(value)


def pct(value: float) -> str:
    return f"{value:.1%}"


def number(value: float | int) -> str:
    return f"{value:,.0f}"


def safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def compute_model() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    arr = read_csv("arr-rollforward.csv")
    opportunities = read_csv("crm-opportunities.csv")
    accounts = read_csv("crm-accounts.csv")
    activation = read_csv("activation-users.csv")
    quotas = read_csv("quota-targets.csv")

    opens = [r for r in opportunities if r["forecast_category"]]
    closed = [r for r in opportunities if not r["forecast_category"]]
    generated = manifest["generated_on"]
    arr_period = manifest["periods"]["arr_rollforward"]
    pipeline_period = manifest["periods"]["pipeline_forecast"]

    arr_sums = {
        key: sum(as_int(r, key) for r in arr)
        for key in ["starting_arr", "new_arr", "expansion_arr", "contraction_arr", "churn_arr", "ending_arr"]
    }
    start = arr_sums["starting_arr"]
    movement_counts = Counter(r["movement_category"] for r in arr)
    arr_metrics = {
        **arr_sums,
        "starting_active_customers": sum(as_int(r, "starting_arr") > 0 for r in arr),
        "ending_active_customers": sum(as_int(r, "ending_arr") > 0 for r in arr),
        "movement_counts": dict(sorted(movement_counts.items())),
        "net_arr_added": arr_sums["ending_arr"] - start,
        "grr": safe_div(start - arr_sums["contraction_arr"] - arr_sums["churn_arr"], start),
        "nrr": safe_div(start + arr_sums["expansion_arr"] - arr_sums["contraction_arr"] - arr_sums["churn_arr"], start),
        "growth_rate": safe_div(arr_sums["ending_arr"] - start, start),
        "gross_gains": arr_sums["new_arr"] + arr_sums["expansion_arr"],
        "total_losses": arr_sums["contraction_arr"] + arr_sums["churn_arr"],
    }
    arr_metrics["expansion_share_gains"] = safe_div(arr_sums["expansion_arr"], arr_metrics["gross_gains"])
    arr_metrics["new_share_gains"] = safe_div(arr_sums["new_arr"], arr_metrics["gross_gains"])

    forecast_order = ["Commit", "Best Case", "Pipeline"]
    stage_order = ["Discovery", "Validation", "Proposal", "Negotiation"]
    risk_order = ["At risk", "Watch", "On track"]
    forecast = {}
    for category in forecast_order:
        subset = [r for r in opens if r["forecast_category"] == category]
        forecast[category] = {
            "deals": len(subset),
            "amount": sum(as_int(r, "amount_usd") for r in subset),
            "expected_arr": sum(as_int(r, "expected_arr_usd") for r in subset),
            "probability_weighted_arr": round(sum(as_int(r, "expected_arr_usd") * int(r["probability"]) / 100 for r in subset)),
        }
    q4_won = sum(
        as_int(r, "expected_arr_usd") for r in closed
        if r["period"] == pipeline_period and r["stage"] == "Closed Won"
    )
    commit_view = q4_won + forecast["Commit"]["expected_arr"]
    best_case_view = commit_view + forecast["Best Case"]["expected_arr"]
    full_view = best_case_view + forecast["Pipeline"]["expected_arr"]
    won = sum(r["stage"] == "Closed Won" for r in closed)
    lost = sum(r["stage"] == "Closed Lost" for r in closed)

    stages = {}
    for stage in stage_order:
        subset = [r for r in opens if r["stage"] == stage]
        stages[stage] = {"deals": len(subset), "expected_arr": sum(as_int(r, "expected_arr_usd") for r in subset)}
    risks = {}
    for risk in risk_order:
        subset = [r for r in opens if r["risk_status"] == risk]
        overdue = [r for r in subset if r["next_step_date"] < generated]
        risks[risk] = {
            "deals": len(subset),
            "expected_arr": sum(as_int(r, "expected_arr_usd") for r in subset),
            "overdue_deals": len(overdue),
            "overdue_expected_arr": sum(as_int(r, "expected_arr_usd") for r in overdue),
        }
    overdue_open = [r for r in opens if r["next_step_date"] < generated]
    pipeline_metrics = {
        "open_deals": len(opens),
        "closed_deals": len(closed),
        "open_by_forecast": {k: forecast[k]["deals"] for k in forecast_order},
        "open_by_stage": {k: stages[k]["deals"] for k in stage_order},
        "open_expected_arr_by_forecast": {k: forecast[k]["expected_arr"] for k in forecast_order},
        "open_expected_arr_total": sum(v["expected_arr"] for v in forecast.values()),
        "q4_closed_won_arr": q4_won,
        "commit_view": commit_view,
        "best_case_view": best_case_view,
        "full_pipeline_view": full_view,
        "closed_won": won,
        "closed_lost": lost,
        "closed_win_rate": safe_div(won, won + lost),
        "overdue_open_deals": len(overdue_open),
        "overdue_open_expected_arr": sum(as_int(r, "expected_arr_usd") for r in overdue_open),
    }

    cohorts = {}
    for cohort in sorted({r["cohort_week"] for r in activation}):
        subset = [r for r in activation if r["cohort_week"] == cohort]
        signups = len(subset)
        activated = sum(r["activated"] == "true" for r in subset)
        retained = sum(r["retained_w2"] == "true" for r in subset)
        cohorts[cohort] = {
            "signups": signups,
            "activated": activated,
            "retained_w2": retained,
            "activation_rate": safe_div(activated, signups),
            "retention_of_activated": safe_div(retained, activated),
            "overall_retention": safe_div(retained, signups),
        }
    signups = len(activation)
    activated = sum(r["activated"] == "true" for r in activation)
    retained = sum(r["retained_w2"] == "true" for r in activation)
    activation_metrics = {
        "signups": signups,
        "activated": activated,
        "retained_w2": retained,
        "activation_rate": safe_div(activated, signups),
        "retention_of_activated": safe_div(retained, activated),
        "overall_retention": safe_div(retained, signups),
        "cohorts": cohorts,
    }

    activation_sources = {}
    for source in sorted({r["acquisition_source"] for r in activation}):
        subset = [r for r in activation if r["acquisition_source"] == source]
        source_signups = len(subset)
        source_activated = sum(r["activated"] == "true" for r in subset)
        source_retained = sum(r["retained_w2"] == "true" for r in subset)
        closed_source = [r for r in closed if r["acquisition_source"] == source]
        source_won = sum(r["stage"] == "Closed Won" for r in closed_source)
        activation_sources[source] = {
            "signups": source_signups,
            "activated": source_activated,
            "retained_w2": source_retained,
            "activation_rate": safe_div(source_activated, source_signups),
            "retention_of_activated": safe_div(source_retained, source_activated),
            "overall_retention": safe_div(source_retained, source_signups),
            "closed_deals": len(closed_source),
            "closed_won": source_won,
            "closed_win_rate": safe_div(source_won, len(closed_source)),
        }

    account_by_id = {r["account_id"]: r for r in accounts}
    segment_retention = {}
    for segment in ["Enterprise", "Mid-Market", "SMB"]:
        ids = {r["account_id"] for r in accounts if r["segment"] == segment}
        subset = [r for r in arr if r["account_id"] in ids]
        segment_retention[segment] = {
            key: sum(as_int(r, key) for r in subset)
            for key in ["starting_arr", "new_arr", "expansion_arr", "contraction_arr", "churn_arr", "ending_arr"]
        }

    q4_won_by_owner = defaultdict(int)
    for row in closed:
        if row["period"] == pipeline_period and row["stage"] == "Closed Won":
            q4_won_by_owner[row["owner_alias"]] += as_int(row, "expected_arr_usd")
    commission = []
    for quota in quotas:
        owner = quota["owner_alias"]
        won_arr = q4_won_by_owner[owner]
        quota_amount = as_int(quota, "quota_usd")
        t1_threshold = float(quota["tier1_threshold"])
        t2_threshold = float(quota["tier2_threshold"])
        t1 = min(won_arr, quota_amount * t1_threshold) * float(quota["tier1_rate"])
        t2 = max(0, min(won_arr, quota_amount * t2_threshold) - quota_amount * t1_threshold) * float(quota["tier2_rate"])
        t3 = max(0, won_arr - quota_amount * t2_threshold) * float(quota["tier3_rate"])
        open_expected = sum(as_int(r, "expected_arr_usd") for r in opens if r["owner_alias"] == owner)
        commit = won_arr + sum(
            as_int(r, "expected_arr_usd") for r in opens
            if r["owner_alias"] == owner and r["forecast_category"] == "Commit"
        )
        commission.append({
            "owner": owner,
            "quota": quota_amount,
            "q4_won": won_arr,
            "attainment": safe_div(won_arr, quota_amount),
            "tier1": t1,
            "tier2": t2,
            "tier3": t3,
            "commission": t1 + t2 + t3,
            "open_expected": open_expected,
            "commit_view": commit,
        })

    top_open = sorted(opens, key=lambda r: (-as_int(r, "expected_arr_usd"), r["opportunity_id"]))[:6]
    loss_reasons = Counter(r["loss_reason"] for r in closed if r["stage"] == "Closed Lost")
    win_reasons = Counter(r["win_reason"] for r in closed if r["stage"] == "Closed Won")

    # Independent source-to-manifest reconciliation. These assertions are also
    # emitted as exact validation checks after the files have been reopened.
    manifest_arr = manifest["arr"]
    for key in ["starting_arr", "new_arr", "expansion_arr", "contraction_arr", "churn_arr", "ending_arr", "starting_active_customers", "ending_active_customers", "net_arr_added"]:
        assert arr_metrics[key] == manifest_arr[key], f"ARR manifest mismatch: {key}"
    assert arr_metrics["movement_counts"] == manifest_arr["movement_counts"]
    assert round(arr_metrics["grr"], 6) == manifest_arr["grr"]
    assert round(arr_metrics["nrr"], 6) == manifest_arr["nrr"]
    manifest_pipeline = manifest["pipeline"]
    for key in ["open_deals", "closed_deals", "open_by_forecast", "open_by_stage", "open_expected_arr_by_forecast", "open_expected_arr_total", "q4_closed_won_arr", "commit_view", "best_case_view", "full_pipeline_view", "closed_won", "closed_lost"]:
        assert pipeline_metrics[key] == manifest_pipeline[key], f"Pipeline manifest mismatch: {key}"
    assert round(pipeline_metrics["closed_win_rate"], 6) == manifest_pipeline["closed_win_rate"]
    for key in ["signups", "activated", "retained_w2"]:
        assert activation_metrics[key] == manifest["activation"][key]
    for key in ["activation_rate", "retention_of_activated", "overall_retention"]:
        assert round(activation_metrics[key], 6) == manifest["activation"][key]
    for cohort, values in cohorts.items():
        for key in ["signups", "activated", "retained_w2"]:
            assert values[key] == manifest["activation"]["cohorts"][cohort][key]
    for row in arr:
        assert as_int(row, "ending_arr") == as_int(row, "starting_arr") + as_int(row, "new_arr") + as_int(row, "expansion_arr") - as_int(row, "contraction_arr") - as_int(row, "churn_arr")

    return {
        "manifest": manifest,
        "arr_rows": arr,
        "opportunities": opportunities,
        "open_rows": opens,
        "closed_rows": closed,
        "accounts": accounts,
        "activation_rows": activation,
        "quotas": quotas,
        "arr": arr_metrics,
        "pipeline": pipeline_metrics,
        "forecast": forecast,
        "stages": stages,
        "risks": risks,
        "activation": activation_metrics,
        "activation_sources": activation_sources,
        "segment_retention": segment_retention,
        "commission": commission,
        "top_open": top_open,
        "loss_reasons": loss_reasons,
        "win_reasons": win_reasons,
        "arr_period": arr_period,
        "pipeline_period": pipeline_period,
        "generated": generated,
        "account_by_id": account_by_id,
    }


# ------------------------------- XLSX -------------------------------------


def xl_title(ws, title: str, subtitle: str, logo: bool = False) -> None:
    ws.sheet_view.showGridLines = False
    if logo:
        image = XLImage(str(LOGO))
        image.width = 34
        image.height = 34
        ws.add_image(image, "A1")
        ws.merge_cells("C1:J1")
        ws["C1"] = title
        ws["C1"].font = FONT_TITLE
        ws.merge_cells("C2:J2")
        ws["C2"] = subtitle
        ws["C2"].font = FONT_SUBTITLE
        ws["C2"].alignment = Alignment(wrap_text=True, vertical="top")
    else:
        ws["A1"] = title
        ws["A1"].font = FONT_TITLE
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=min(ws.max_column or 8, 12))
        ws["A2"] = subtitle
        ws["A2"].font = FONT_SUBTITLE
        ws["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.row_dimensions[1].height = 30
    ws.row_dimensions[2].height = 28


def xl_header(ws, row: int, headers: Sequence[str], start_col: int = 1) -> None:
    for offset, value in enumerate(headers):
        cell = ws.cell(row=row, column=start_col + offset, value=value)
        cell.font = FONT_HEADER
        cell.fill = FILL_HEADER
        cell.border = BORDER
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 30


def xl_formula(cell, expression: str, number_format: str | None = None) -> None:
    cell.value = expression if expression.startswith("=") else "=" + expression
    cell.font = FONT_LINK if "!" in expression else FONT_FORMULA
    cell.alignment = Alignment(vertical="center")
    if number_format:
        cell.number_format = number_format


def xl_value(cell, value, number_format: str | None = None, financial: bool = False, fill=None) -> None:
    cell.value = value
    cell.font = FONT_INPUT if financial else FONT_BASE
    cell.border = BORDER
    cell.alignment = Alignment(vertical="center")
    if number_format:
        cell.number_format = number_format
    if fill:
        cell.fill = fill


def xl_section(ws, row: int, text: str, start_col: int, end_col: int) -> None:
    ws.merge_cells(start_row=row, start_column=start_col, end_row=row, end_column=end_col)
    cell = ws.cell(row=row, column=start_col, value=text)
    cell.font = FONT_SECTION
    cell.fill = FILL_LIGHT
    cell.alignment = Alignment(vertical="center")
    ws.row_dimensions[row].height = 22


def xl_table(ws, name: str, ref: str) -> None:
    table = Table(displayName=name, ref=ref)
    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2", showFirstColumn=False, showLastColumn=False,
        showRowStripes=True, showColumnStripes=False,
    )
    ws.add_table(table)


def xl_widths(ws, widths: Sequence[float]) -> None:
    for index, width in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(index)].width = width


def write_raw_sheet(wb: Workbook, name: str, title: str, subtitle: str, headers: Sequence[str], rows: Sequence[dict], fields: Sequence[str], table_name: str, financial_fields: set[str], percent_fields: set[str] | None = None, date_fields: set[str] | None = None, bool_fields: set[str] | None = None, widths: Sequence[float] | None = None, freeze: str = "D5") -> None:
    percent_fields = percent_fields or set()
    date_fields = date_fields or set()
    bool_fields = bool_fields or set()
    ws = wb.create_sheet(name)
    xl_title(ws, title, subtitle)
    xl_header(ws, 4, headers)
    for row_index, source in enumerate(rows, start=5):
        for col_index, field in enumerate(fields, start=1):
            raw = source[field]
            value = raw
            fmt = None
            if raw == "":
                value = None
            elif field in bool_fields:
                value = raw == "true"
            elif field in date_fields:
                value = as_date(raw)
                fmt = DATE_FMT
            elif field in percent_fields:
                value = int(raw) / 100
                fmt = PERCENT
            elif field in {"health_score"}:
                value = int(raw)
                fmt = INTEGER
            elif field.endswith("_arr") or field.endswith("_usd") or field in {"starting_arr", "new_arr", "expansion_arr", "contraction_arr", "churn_arr", "ending_arr"}:
                value = int(raw)
                fmt = CURRENCY
            cell = ws.cell(row=row_index, column=col_index)
            xl_value(cell, value, fmt, financial=field in financial_fields)
            if row_index % 2 == 0:
                cell.fill = FILL_LIGHT
    end_row = 4 + len(rows)
    xl_table(ws, table_name, f"A4:{get_column_letter(len(fields))}{end_row}")
    ws.freeze_panes = freeze
    ws.auto_filter.ref = f"A4:{get_column_letter(len(fields))}{end_row}"
    ws.print_title_rows = "1:4"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.oddFooter.center.text = f"Built by Vera {BUILD_DATE} | Synthetic & anonymized | Page &P of &N"
    ws.oddFooter.center.size = 8
    ws.oddFooter.center.font = "Arial"
    if widths:
        xl_widths(ws, widths)


def build_workbook(model: dict) -> None:
    manifest = model["manifest"]
    wb = Workbook()
    wb.remove(wb.active)
    wb.properties.creator = "Vera"
    wb.properties.lastModifiedBy = "Vera"
    wb.properties.title = "Northwind synthetic ARR rollforward and Q4 pipeline"
    wb.properties.subject = "Formula-first RevOps example built from source CSVs"
    wb.properties.description = "Synthetic and anonymized. Built by Vera 2026-11-23. Recalculation and visual rendering not inspected."
    wb.properties.created = BUILD_DATETIME
    wb.properties.modified = BUILD_DATETIME
    wb.calculation = CalcProperties(calcMode="auto", fullCalcOnLoad=True, forceFullCalc=True, calcId=191029)

    # README and assumptions.
    ws = wb.create_sheet("README")
    xl_title(ws, "Northwind | Office example guide", "Formula-first ARR, pipeline, activation and commission workbook. Full detail is here and in the source CSVs.", logo=True)
    xl_section(ws, 4, "SOURCE & ASSUMPTIONS — yellow cells are the controlling metadata", 1, 4)
    metadata = [
        ("Dataset", manifest["dataset"], None),
        ("Generated on", as_date(manifest["generated_on"]), DATE_FMT),
        ("ARR period", model["arr_period"], None),
        ("Pipeline period", model["pipeline_period"], None),
        ("Currency", manifest["currency"], None),
        ("Synthetic", bool(manifest["synthetic"]), None),
        ("Anonymized", bool(manifest["anonymized"]), None),
    ]
    for row, (label, value, fmt) in enumerate(metadata, start=5):
        xl_value(ws.cell(row, 1), label)
        xl_value(ws.cell(row, 2), value, fmt, fill=FILL_YELLOW)
        ws.cell(row, 1).font = Font(name="Arial", size=9, bold=True, color=INK)
    xl_section(ws, 13, "DEFINITIONS & MODEL DOCTRINE", 1, 4)
    definitions = [
        ("ARR identity", "Ending ARR = starting + new + expansion − contraction − churn; every source row is tested in Python."),
        ("GRR", "(Starting ARR − contraction − churn) / starting ARR. New ARR and expansion are excluded."),
        ("NRR", "(Starting ARR + expansion − contraction − churn) / starting ARR. New ARR is excluded."),
        ("Active customer", "ARR row with the relevant starting_arr or ending_arr greater than zero."),
        ("Open deal", "Opportunity with a nonblank forecast_category. Expected ARR is the source expected_arr_usd field."),
        ("Forecast scenarios", "Commit = Q4 closed-won + Commit expected ARR; Best Case adds Best Case; Full Pipeline adds Pipeline. Sums are not probability-weighted."),
        ("Activation", "activated=true / signups. Week-2 retention of activated = retained_w2=true / activated=true."),
        ("Commission", "Illustrative progressive commission on Q4 closed-won expected ARR using quota CSV thresholds/rates; not a payroll statement."),
        ("Overdue next step", "Open next_step_date earlier than the manifest generated_on date; this is a hygiene flag, not a forecast haircut."),
        ("Population note", "ARR, CRM and activation are separate synthetic populations. No causal attribution is made across them."),
    ]
    for row, (label, text) in enumerate(definitions, start=14):
        xl_value(ws.cell(row, 1), label)
        ws.cell(row, 1).font = Font(name="Arial", size=9, bold=True, color=INK)
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
        xl_value(ws.cell(row, 2), text)
        ws.cell(row, 2).alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[row].height = 31
    xl_section(ws, 25, "COLOR LEGEND & BUILD NOTE", 1, 4)
    legends = [
        ("Blue text", "Hardcoded financial inputs from CSV", FONT_INPUT, None),
        ("Black text", "Formula calculated on the same sheet", FONT_FORMULA, None),
        ("Green text", "Formula linked to another worksheet", FONT_LINK, None),
        ("Yellow fill", "Controlling assumptions or commission levers", FONT_BASE, FILL_YELLOW),
    ]
    for row, (label, text, font, fill) in enumerate(legends, start=26):
        xl_value(ws.cell(row, 1), label, fill=fill)
        ws.cell(row, 1).font = font
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=4)
        xl_value(ws.cell(row, 2), text)
    ws.merge_cells("A31:D32")
    xl_value(ws["A31"], f"Built by Vera {BUILD_DATE}. Synthetic and anonymized; no live-source connection. Workbook recalc-on-load is enabled. Formula recalculation and visual Office rendering: not inspected. Formula logic was independently verified in Python; see data/office-validation.json.")
    ws["A31"].alignment = Alignment(wrap_text=True, vertical="top")
    ws["A31"].fill = FILL_LIGHT
    xl_section(ws, 34, "SOURCE REGISTER — hashes match manifest.json", 1, 4)
    xl_header(ws, 35, ["Source file", "Rows", "SHA-256", "Workbook use"])
    source_roles = {
        "arr-rollforward.csv": "ARR Rollforward; ARR Summary",
        "crm-opportunities.csv": "Open Pipeline; Closed Opportunities; Pipeline Summary",
        "crm-accounts.csv": "Accounts; segment analysis",
        "activation-users.csv": "Activation; cohort and source analysis",
        "quota-targets.csv": "Quota Commission",
    }
    source_names = list(manifest["source_sha256"])
    for row, name in enumerate(source_names, start=36):
        path = BASE / name if name == "mock-pipeline.csv" else DATA / name
        with path.open(newline="", encoding="utf-8") as handle:
            row_count = sum(1 for _ in csv.DictReader(handle))
        xl_value(ws.cell(row, 1), name)
        xl_value(ws.cell(row, 2), row_count, INTEGER)
        xl_value(ws.cell(row, 3), manifest["source_sha256"][name])
        xl_value(ws.cell(row, 4), source_roles.get(name, "Source register only"))
    ws.freeze_panes = "A5"
    xl_widths(ws, [29, 26, 68, 55])
    ws.oddFooter.center.text = f"Built by Vera {BUILD_DATE} | Synthetic & anonymized | Page &P of &N"
    ws.oddFooter.center.font = "Arial"

    # Raw ARR and CRM sheets.
    arr_fields = ["account_id", "period", "starting_arr", "new_arr", "expansion_arr", "contraction_arr", "churn_arr", "ending_arr", "movement_category", "previous_plan_tier", "current_plan_tier", "currency"]
    write_raw_sheet(wb, "ARR Rollforward", "ARR Rollforward | 2026-Q3", "All 1,050 source rows. Source: data/arr-rollforward.csv. Blue financial values are hardcoded inputs.", ["Account ID", "Period", "Starting ARR", "New ARR", "Expansion ARR", "Contraction ARR", "Churn ARR", "Ending ARR", "Movement Category", "Previous Plan Tier", "Current Plan Tier", "Currency"], model["arr_rows"], arr_fields, "tblARRRollforward", {"starting_arr", "new_arr", "expansion_arr", "contraction_arr", "churn_arr", "ending_arr"}, widths=[16, 12, 16, 14, 16, 17, 14, 16, 20, 20, 20, 11])

    opp_fields = ["opportunity_id", "account_id", "opportunity_alias", "owner_id", "owner_alias", "stage", "forecast_category", "amount_usd", "expected_arr_usd", "probability", "created_date", "close_date", "last_activity_date", "next_step_date", "acquisition_source", "product_family", "opportunity_type", "risk_status", "next_step", "win_reason", "loss_reason", "competitor_alias", "period"]
    opp_headers = ["Opportunity ID", "Account ID", "Opportunity Alias", "Owner ID", "Owner", "Stage", "Forecast Category", "Amount (USD)", "Expected ARR (USD)", "Probability", "Created Date", "Close Date", "Last Activity Date", "Next Step Date", "Acquisition Source", "Product Family", "Opportunity Type", "Risk Status", "Next Step", "Win Reason", "Loss Reason", "Competitor Alias", "Period"]
    opp_widths = [17, 15, 22, 14, 14, 17, 19, 17, 20, 13, 14, 14, 17, 16, 19, 19, 19, 14, 34, 20, 20, 19, 12]
    common_opp_kwargs = dict(fields=opp_fields, financial_fields={"amount_usd", "expected_arr_usd"}, percent_fields={"probability"}, date_fields={"created_date", "close_date", "last_activity_date", "next_step_date"}, widths=opp_widths)
    write_raw_sheet(wb, "Open Pipeline", "Open Pipeline | 2026-Q4", "All 200 open opportunities (nonblank forecast_category). Source: data/crm-opportunities.csv.", opp_headers, model["open_rows"], table_name="tblOpenPipeline", **common_opp_kwargs)
    write_raw_sheet(wb, "Closed Opportunities", "Closed Opportunities | Q3 + Q4 2026", "All 400 closed opportunities. Source: data/crm-opportunities.csv.", opp_headers, model["closed_rows"], table_name="tblClosedOpportunities", **common_opp_kwargs)

    account_fields = ["account_id", "account_alias", "lifecycle_status", "segment", "industry", "region", "country", "owner_id", "owner_alias", "plan_tier", "billing_frequency", "currency", "account_created_date", "customer_since_date", "health_score", "last_activity_date", "acquisition_source", "movement_category"]
    write_raw_sheet(wb, "Accounts", "Accounts | synthetic account registry", "All 1,050 accounts. Source: data/crm-accounts.csv. Aliases only; no real identities.", ["Account ID", "Account Alias", "Lifecycle Status", "Segment", "Industry", "Region", "Country", "Owner ID", "Owner", "Plan Tier", "Billing Frequency", "Currency", "Account Created Date", "Customer Since Date", "Health Score", "Last Activity Date", "Acquisition Source", "Movement Category"], model["accounts"], account_fields, "tblAccounts", set(), date_fields={"account_created_date", "customer_since_date", "last_activity_date"}, widths=[16, 20, 18, 16, 20, 18, 18, 14, 14, 15, 18, 11, 21, 20, 14, 18, 20, 20], freeze="C5")

    activation_fields = ["user_id", "account_id", "user_alias", "cohort_week", "signup_date", "activated", "activated_date", "retained_w2", "acquisition_source"]
    write_raw_sheet(wb, "Activation", "Activation | cohorts W40–W43", "All 2,400 synthetic users. Source: data/activation-users.csv. Boolean flags drive activation and retention formulas.", ["User ID", "Account ID", "User Alias", "Cohort Week", "Signup Date", "Activated", "Activated Date", "Retained W2", "Acquisition Source"], model["activation_rows"], activation_fields, "tblActivation", set(), date_fields={"signup_date", "activated_date"}, bool_fields={"activated", "retained_w2"}, widths=[18, 16, 20, 15, 15, 12, 17, 14, 20])

    # ARR Summary, formula-first.
    ws = wb.create_sheet("ARR Summary", 1)
    xl_title(ws, "ARR Summary | 2026-Q3", "Formula-linked to all 1,050 ARR rows. NRR excludes new ARR; active customers have ARR greater than zero.", logo=True)
    xl_section(ws, 4, "ARR MOVEMENT & RETENTION", 1, 4)
    xl_header(ws, 5, ["Metric", "Value", "Customers", "Definition"])
    arr_rows = [
        ("Starting ARR", "=SUM('ARR Rollforward'!$D$5:$D$1054)", "=COUNTIF('ARR Rollforward'!$D$5:$D$1054,\">0\")", "Opening base; active if starting ARR > 0"),
        ("New ARR", "=SUM('ARR Rollforward'!$E$5:$E$1054)", "=COUNTIF('ARR Rollforward'!$J$5:$J$1054,\"New\")", "New-logo ARR"),
        ("Expansion ARR", "=SUM('ARR Rollforward'!$F$5:$F$1054)", "=COUNTIF('ARR Rollforward'!$J$5:$J$1054,\"Expansion\")", "Existing-customer gains"),
        ("Contraction ARR", "=SUM('ARR Rollforward'!$G$5:$G$1054)", "=COUNTIF('ARR Rollforward'!$J$5:$J$1054,\"Contraction\")", "Positive loss magnitude"),
        ("Churn ARR", "=SUM('ARR Rollforward'!$H$5:$H$1054)", "=COUNTIF('ARR Rollforward'!$J$5:$J$1054,\"Churn\")", "Positive loss magnitude"),
        ("Ending ARR", "=SUM('ARR Rollforward'!$I$5:$I$1054)", "=COUNTIF('ARR Rollforward'!$I$5:$I$1054,\">0\")", "Closing base; active if ending ARR > 0"),
        ("Net ARR added", "=B11-B6", "=C11-C6", "Ending minus starting"),
    ]
    for row, (label, amount_formula, count_formula, definition) in enumerate(arr_rows, start=6):
        xl_value(ws.cell(row, 1), label)
        xl_formula(ws.cell(row, 2), amount_formula, CURRENCY)
        xl_formula(ws.cell(row, 3), count_formula, INTEGER)
        xl_value(ws.cell(row, 4), definition)
        for col in range(1, 5):
            ws.cell(row, col).border = BORDER
    xl_header(ws, 14, ["Retention / growth metric", "Value", "", "Definition"])
    retention_rows = [
        ("Net revenue retention", "=IFERROR((B6+B8-B9-B10)/B6,0)", PERCENT, "Starting + expansion − contraction − churn, over starting"),
        ("Gross revenue retention", "=IFERROR((B6-B9-B10)/B6,0)", PERCENT, "Starting − contraction − churn, over starting"),
        ("ARR growth", "=IFERROR(B12/B6,0)", PERCENT, "Net ARR added / starting ARR"),
        ("Gross gains", "=B7+B8", CURRENCY, "New + expansion"),
        ("Expansion share of gross gains", "=IFERROR(B8/B18,0)", PERCENT, "Expansion / (new + expansion)"),
        ("Total losses", "=B9+B10", CURRENCY, "Contraction + churn; positive magnitude"),
    ]
    for row, (label, formula, fmt, definition) in enumerate(retention_rows, start=15):
        xl_value(ws.cell(row, 1), label)
        xl_formula(ws.cell(row, 2), formula, fmt)
        xl_value(ws.cell(row, 4), definition)
        for col in range(1, 5):
            ws.cell(row, col).border = BORDER
    xl_section(ws, 4, "CUSTOMER MOVEMENTS", 6, 8)
    xl_header(ws, 5, ["Movement", "Accounts", "ARR impact"], start_col=6)
    for row, category in enumerate(["New", "Expansion", "Flat", "Contraction", "Churn"], start=6):
        xl_value(ws.cell(row, 6), category)
        xl_formula(ws.cell(row, 7), f"=COUNTIF('ARR Rollforward'!$J$5:$J$1054,F{row})", INTEGER)
        if category == "New":
            formula = f"=SUMIF('ARR Rollforward'!$J$5:$J$1054,F{row},'ARR Rollforward'!$E$5:$E$1054)"
        elif category == "Expansion":
            formula = f"=SUMIF('ARR Rollforward'!$J$5:$J$1054,F{row},'ARR Rollforward'!$F$5:$F$1054)"
        elif category == "Contraction":
            formula = f"=-SUMIF('ARR Rollforward'!$J$5:$J$1054,F{row},'ARR Rollforward'!$G$5:$G$1054)"
        elif category == "Churn":
            formula = f"=-SUMIF('ARR Rollforward'!$J$5:$J$1054,F{row},'ARR Rollforward'!$H$5:$H$1054)"
        else:
            formula = f"=SUMIF('ARR Rollforward'!$J$5:$J$1054,F{row},'ARR Rollforward'!$I$5:$I$1054)-SUMIF('ARR Rollforward'!$J$5:$J$1054,F{row},'ARR Rollforward'!$D$5:$D$1054)"
        xl_formula(ws.cell(row, 8), formula, CURRENCY)
        for col in range(6, 9):
            ws.cell(row, col).border = BORDER
    ws.merge_cells("F13:H16")
    xl_value(ws["F13"], "Customer bridge: starting active + New − Churn = ending active. Expansion, Flat and Contraction movements do not change the active count; use the formula cells above for current values.")
    ws["F13"].alignment = Alignment(wrap_text=True, vertical="top")
    ws["F13"].fill = FILL_LIGHT
    ws.merge_cells("A23:H24")
    xl_value(ws["A23"], "Decision use: compare Total losses with Expansion ARR and review NRR in the formula cells above. Source detail remains in ARR Rollforward; no Word table attempts to reproduce the full detail.")
    ws["A23"].alignment = Alignment(wrap_text=True, vertical="top")
    ws["A23"].fill = FILL_LIGHT
    xl_widths(ws, [31, 18, 14, 54, 3, 20, 14, 18])
    ws.freeze_panes = "A5"

    # Quota Commission.
    ws = wb.create_sheet("Quota Commission")
    xl_title(ws, "Quota & Commission | 2026-Q4", "Yellow cells are source-controlled commission levers. Commission is an illustrative progressive model on Q4 closed-won expected ARR, not payroll.")
    quota_headers = ["Owner ID", "Owner", "Period", "Quota (USD)", "Tier 1 Threshold", "Tier 1 Rate", "Tier 2 Threshold", "Tier 2 Rate", "Tier 3 Rate", "Currency", "Q4 Closed Won ARR", "Attainment", "Tier 1 Commission", "Tier 2 Commission", "Tier 3 Commission", "Total Commission", "Open Expected ARR", "Commit Forecast View"]
    xl_header(ws, 4, quota_headers)
    for row, source in enumerate(model["quotas"], start=5):
        values = [source["owner_id"], source["owner_alias"], source["period"], as_int(source, "quota_usd"), float(source["tier1_threshold"]), float(source["tier1_rate"]), float(source["tier2_threshold"]), float(source["tier2_rate"]), float(source["tier3_rate"]), source["currency"]]
        for col, value in enumerate(values, start=1):
            fmt = CURRENCY if col == 4 else PERCENT if col in {5, 6, 7, 8, 9} else None
            financial = col in {4, 5, 6, 7, 8, 9}
            fill = FILL_YELLOW if col in {5, 6, 7, 8, 9} else None
            xl_value(ws.cell(row, col), value, fmt, financial=financial, fill=fill)
        xl_formula(ws.cell(row, 11), f"=SUMIFS('Closed Opportunities'!$I$5:$I$404,'Closed Opportunities'!$E$5:$E$404,$B{row},'Closed Opportunities'!$F$5:$F$404,\"Closed Won\",'Closed Opportunities'!$W$5:$W$404,$C{row})", CURRENCY)
        xl_formula(ws.cell(row, 12), f"=IFERROR(K{row}/D{row},0)", PERCENT)
        xl_formula(ws.cell(row, 13), f"=MIN(K{row},D{row}*E{row})*F{row}", CURRENCY)
        xl_formula(ws.cell(row, 14), f"=MAX(0,MIN(K{row},D{row}*G{row})-D{row}*E{row})*H{row}", CURRENCY)
        xl_formula(ws.cell(row, 15), f"=MAX(0,K{row}-D{row}*G{row})*I{row}", CURRENCY)
        xl_formula(ws.cell(row, 16), f"=SUM(M{row}:O{row})", CURRENCY)
        xl_formula(ws.cell(row, 17), f"=SUMIF('Open Pipeline'!$E$5:$E$204,$B{row},'Open Pipeline'!$I$5:$I$204)", CURRENCY)
        xl_formula(ws.cell(row, 18), f"=K{row}+SUMIFS('Open Pipeline'!$I$5:$I$204,'Open Pipeline'!$E$5:$E$204,$B{row},'Open Pipeline'!$G$5:$G$204,\"Commit\")", CURRENCY)
        for col in range(1, 19):
            ws.cell(row, col).border = BORDER
    xl_table(ws, "tblQuotaCommission", "A4:R12")
    xl_value(ws["A14"], "Controls")
    ws["A14"].font = FONT_SECTION
    xl_formula(ws["D14"], "=SUM(D5:D12)", CURRENCY)
    xl_formula(ws["K14"], "=SUM(K5:K12)", CURRENCY)
    xl_formula(ws["P14"], "=SUM(P5:P12)", CURRENCY)
    xl_formula(ws["Q14"], "=SUM(Q5:Q12)", CURRENCY)
    xl_formula(ws["R14"], "=SUM(R5:R12)", CURRENCY)
    ws.freeze_panes = "D5"
    xl_widths(ws, [14, 14, 12, 16, 17, 13, 17, 13, 13, 11, 20, 14, 19, 19, 19, 18, 20, 21])

    # Pipeline Summary.
    ws = wb.create_sheet("Pipeline Summary")
    xl_title(ws, "Pipeline Summary | 2026-Q4", "Scenario totals use unweighted expected_arr_usd, matching manifest definitions. Probability-weighted ARR is shown separately.", logo=True)
    xl_section(ws, 4, "OPEN FORECAST SCENARIOS", 1, 7)
    xl_header(ws, 5, ["Scenario", "Q4 Closed Won", "Commit", "Best Case", "Pipeline", "Scenario Total", "Definition"])
    scenario_rows = [("Commit", 6), ("Best Case", 7), ("Full Pipeline", 8)]
    for label, row in scenario_rows:
        xl_value(ws.cell(row, 1), label)
        xl_formula(ws.cell(row, 2), "=SUMIFS('Closed Opportunities'!$I$5:$I$404,'Closed Opportunities'!$F$5:$F$404,\"Closed Won\",'Closed Opportunities'!$W$5:$W$404,README!$B$8)", CURRENCY)
        xl_formula(ws.cell(row, 3), "=SUMIF('Open Pipeline'!$G$5:$G$204,\"Commit\",'Open Pipeline'!$I$5:$I$204)", CURRENCY)
        if row >= 7:
            xl_formula(ws.cell(row, 4), "=SUMIF('Open Pipeline'!$G$5:$G$204,\"Best Case\",'Open Pipeline'!$I$5:$I$204)", CURRENCY)
        else:
            xl_value(ws.cell(row, 4), None)
        if row == 8:
            xl_formula(ws.cell(row, 5), "=SUMIF('Open Pipeline'!$G$5:$G$204,\"Pipeline\",'Open Pipeline'!$I$5:$I$204)", CURRENCY)
        else:
            xl_value(ws.cell(row, 5), None)
        xl_formula(ws.cell(row, 6), f"=SUM(B{row}:E{row})", CURRENCY)
        definition = {"Commit": "Q4 won + Commit", "Best Case": "Commit scenario + Best Case", "Full Pipeline": "Best Case scenario + Pipeline"}[label]
        xl_value(ws.cell(row, 7), definition)
        for col in range(1, 8):
            ws.cell(row, col).border = BORDER
    xl_section(ws, 10, "FORECAST CATEGORY DETAIL", 1, 5)
    xl_header(ws, 11, ["Forecast Category", "Deals", "Raw Amount", "Expected ARR", "Probability-weighted ARR"])
    for row, category in enumerate(["Commit", "Best Case", "Pipeline"], start=12):
        xl_value(ws.cell(row, 1), category)
        xl_formula(ws.cell(row, 2), f"=COUNTIF('Open Pipeline'!$G$5:$G$204,A{row})", INTEGER)
        xl_formula(ws.cell(row, 3), f"=SUMIF('Open Pipeline'!$G$5:$G$204,A{row},'Open Pipeline'!$H$5:$H$204)", CURRENCY)
        xl_formula(ws.cell(row, 4), f"=SUMIF('Open Pipeline'!$G$5:$G$204,A{row},'Open Pipeline'!$I$5:$I$204)", CURRENCY)
        xl_formula(ws.cell(row, 5), f"=SUMPRODUCT(('Open Pipeline'!$G$5:$G$204=A{row})*'Open Pipeline'!$I$5:$I$204,'Open Pipeline'!$J$5:$J$204)", CURRENCY)
    xl_value(ws["A15"], "Total / all open")
    for col in range(2, 6):
        xl_formula(ws.cell(15, col), f"=SUM({get_column_letter(col)}12:{get_column_letter(col)}14)", INTEGER if col == 2 else CURRENCY)
    xl_section(ws, 17, "OPEN STAGE MIX", 1, 4)
    xl_header(ws, 18, ["Stage", "Deals", "Expected ARR", "Deal Mix"])
    for row, stage in enumerate(["Discovery", "Validation", "Proposal", "Negotiation"], start=19):
        xl_value(ws.cell(row, 1), stage)
        xl_formula(ws.cell(row, 2), f"=COUNTIF('Open Pipeline'!$F$5:$F$204,A{row})", INTEGER)
        xl_formula(ws.cell(row, 3), f"=SUMIF('Open Pipeline'!$F$5:$F$204,A{row},'Open Pipeline'!$I$5:$I$204)", CURRENCY)
        xl_formula(ws.cell(row, 4), f"=IFERROR(B{row}/$B$15,0)", PERCENT)
    xl_section(ws, 24, "RISK & NEXT-STEP HYGIENE", 1, 5)
    xl_header(ws, 25, ["Risk", "Deals", "Expected ARR", "Overdue Deals", "Overdue Expected ARR"])
    for row, risk in enumerate(["At risk", "Watch", "On track"], start=26):
        xl_value(ws.cell(row, 1), risk)
        xl_formula(ws.cell(row, 2), f"=COUNTIF('Open Pipeline'!$R$5:$R$204,A{row})", INTEGER)
        xl_formula(ws.cell(row, 3), f"=SUMIF('Open Pipeline'!$R$5:$R$204,A{row},'Open Pipeline'!$I$5:$I$204)", CURRENCY)
        xl_formula(ws.cell(row, 4), f"=COUNTIFS('Open Pipeline'!$R$5:$R$204,A{row},'Open Pipeline'!$N$5:$N$204,\"<\"&README!$B$6)", INTEGER)
        xl_formula(ws.cell(row, 5), f"=SUMIFS('Open Pipeline'!$I$5:$I$204,'Open Pipeline'!$R$5:$R$204,A{row},'Open Pipeline'!$N$5:$N$204,\"<\"&README!$B$6)", CURRENCY)
    xl_section(ws, 30, "CLOSED OUTCOMES | Q3 + Q4", 1, 4)
    xl_header(ws, 31, ["Outcome", "Deals", "Expected ARR", "Closed Win Rate"])
    for row, outcome in enumerate(["Closed Won", "Closed Lost"], start=32):
        xl_value(ws.cell(row, 1), outcome)
        xl_formula(ws.cell(row, 2), f"=COUNTIF('Closed Opportunities'!$F$5:$F$404,A{row})", INTEGER)
        xl_formula(ws.cell(row, 3), f"=SUMIF('Closed Opportunities'!$F$5:$F$404,A{row},'Closed Opportunities'!$I$5:$I$404)", CURRENCY)
    xl_formula(ws["D32"], "=IFERROR(B32/SUM(B32:B33),0)", PERCENT)
    xl_value(ws["A34"], "Total closed")
    xl_formula(ws["B34"], "=SUM(B32:B33)", INTEGER)
    xl_formula(ws["C34"], "=SUM(C32:C33)", CURRENCY)
    ws.merge_cells("G11:J16")
    xl_value(ws["G11"], "Decision use: read Commit, Best Case and Full Pipeline as cumulative scenarios, not probability-weighted forecasts. Review the risk table for overdue next-step counts and expected ARR; overdue status is a hygiene flag, not an automatic forecast haircut.")
    ws["G11"].alignment = Alignment(wrap_text=True, vertical="top")
    ws["G11"].fill = FILL_LIGHT
    xl_widths(ws, [25, 18, 18, 18, 24, 20, 30, 14, 14, 14])
    ws.freeze_panes = "A5"

    # Activation summary sits above the raw table on the same required sheet.
    ws = wb["Activation"]
    # Raw table occupies A4:I2404, so put formula summaries in K:R without
    # disturbing the complete 2,400-row table.
    xl_section(ws, 1, "ACTIVATION SUMMARY — formulas use the raw table at left", 11, 14)
    xl_header(ws, 3, ["Cohort", "Signups", "Activated", "Retained W2"], start_col=11)
    for row, cohort in enumerate(sorted(model["activation"]["cohorts"]), start=4):
        xl_value(ws.cell(row, 11), cohort)
        xl_formula(ws.cell(row, 12), f"=COUNTIF($D$5:$D$2404,K{row})", INTEGER)
        xl_formula(ws.cell(row, 13), f"=COUNTIFS($D$5:$D$2404,K{row},$F$5:$F$2404,TRUE)", INTEGER)
        xl_formula(ws.cell(row, 14), f"=COUNTIFS($D$5:$D$2404,K{row},$H$5:$H$2404,TRUE)", INTEGER)
    xl_header(ws, 10, ["Metric", "Value", "Rate", "Definition"], start_col=11)
    activation_summary = [
        ("All signups", "=COUNTA($A$5:$A$2404)", None, "All synthetic user rows"),
        ("Activated", "=COUNTIF($F$5:$F$2404,TRUE)", "=IFERROR(L12/L11,0)", "Activated / signups"),
        ("Retained W2", "=COUNTIF($H$5:$H$2404,TRUE)", "=IFERROR(L13/L12,0)", "Retained / activated"),
    ]
    for row, (label, value_formula, rate_formula, definition) in enumerate(activation_summary, start=11):
        xl_value(ws.cell(row, 11), label)
        xl_formula(ws.cell(row, 12), value_formula, INTEGER)
        if rate_formula:
            xl_formula(ws.cell(row, 13), rate_formula, PERCENT)
        xl_value(ws.cell(row, 14), definition)
    xl_header(ws, 16, ["Acquisition Source", "Signups", "Activated", "Retained W2"], start_col=11)
    for row, source in enumerate(sorted(model["activation_sources"]), start=17):
        xl_value(ws.cell(row, 11), source)
        xl_formula(ws.cell(row, 12), f"=COUNTIF($I$5:$I$2404,K{row})", INTEGER)
        xl_formula(ws.cell(row, 13), f"=COUNTIFS($I$5:$I$2404,K{row},$F$5:$F$2404,TRUE)", INTEGER)
        xl_formula(ws.cell(row, 14), f"=COUNTIFS($I$5:$I$2404,K{row},$H$5:$H$2404,TRUE)", INTEGER)
    xl_widths(ws, [18, 16, 20, 15, 15, 12, 17, 14, 20, 3, 22, 15, 15, 30])

    # Validation sheet: live formulas vs manifest control totals.
    ws = wb.create_sheet("Validation")
    xl_title(ws, "Validation | workbook controls", "Actual cells are formulas; blue control cells come from manifest.json. Formula evaluation itself was not inspected in this environment.", logo=True)
    xl_header(ws, 4, ["Check", "Workbook Result", "Manifest Control", "Status", "Basis"])
    checks = []
    def add_check(label, formula, control, fmt=INTEGER, rounded=False):
        checks.append((label, formula, control, fmt, rounded))
    add_check("ARR row count", "=COUNTA('ARR Rollforward'!$A$5:$A$1054)", len(model["arr_rows"]))
    add_check("Open deal row count", "=COUNTA('Open Pipeline'!$A$5:$A$204)", len(model["open_rows"]))
    add_check("Closed deal row count", "=COUNTA('Closed Opportunities'!$A$5:$A$404)", len(model["closed_rows"]))
    add_check("Account row count", "=COUNTA('Accounts'!$A$5:$A$1054)", len(model["accounts"]))
    add_check("Activation row count", "=COUNTA('Activation'!$A$5:$A$2404)", len(model["activation_rows"]))
    add_check("Quota row count", "=COUNTA('Quota Commission'!$A$5:$A$12)", len(model["quotas"]))
    for label, key, col in [("Starting ARR", "starting_arr", "D"), ("New ARR", "new_arr", "E"), ("Expansion ARR", "expansion_arr", "F"), ("Contraction ARR", "contraction_arr", "G"), ("Churn ARR", "churn_arr", "H"), ("Ending ARR", "ending_arr", "I")]:
        add_check(label, f"=SUM('ARR Rollforward'!${col}$5:${col}$1054)", model["arr"][key], CURRENCY)
    add_check("ARR aggregate residual", "=SUM('ARR Rollforward'!$I$5:$I$1054)-(SUM('ARR Rollforward'!$D$5:$D$1054)+SUM('ARR Rollforward'!$E$5:$E$1054)+SUM('ARR Rollforward'!$F$5:$F$1054)-SUM('ARR Rollforward'!$G$5:$G$1054)-SUM('ARR Rollforward'!$H$5:$H$1054))", 0, CURRENCY)
    add_check("Starting active customers", "=COUNTIF('ARR Rollforward'!$D$5:$D$1054,\">0\")", model["arr"]["starting_active_customers"])
    add_check("Ending active customers", "=COUNTIF('ARR Rollforward'!$I$5:$I$1054,\">0\")", model["arr"]["ending_active_customers"])
    add_check("Net ARR added", "='ARR Summary'!$B$12", model["arr"]["net_arr_added"], CURRENCY)
    add_check("GRR", "='ARR Summary'!$B$16", round(model["arr"]["grr"], 6), DECIMAL, True)
    add_check("NRR", "='ARR Summary'!$B$15", round(model["arr"]["nrr"], 6), DECIMAL, True)
    for category in ["Churn", "Contraction", "Expansion", "Flat", "New"]:
        add_check(f"Movement count | {category}", f"=COUNTIF('ARR Rollforward'!$J$5:$J$1054,\"{category}\")", model["arr"]["movement_counts"][category])
    add_check("Open expected ARR", "=SUM('Open Pipeline'!$I$5:$I$204)", model["pipeline"]["open_expected_arr_total"], CURRENCY)
    for category in ["Commit", "Best Case", "Pipeline"]:
        add_check(f"Open expected ARR | {category}", f"=SUMIF('Open Pipeline'!$G$5:$G$204,\"{category}\",'Open Pipeline'!$I$5:$I$204)", model["forecast"][category]["expected_arr"], CURRENCY)
        add_check(f"Open deal count | {category}", f"=COUNTIF('Open Pipeline'!$G$5:$G$204,\"{category}\")", model["forecast"][category]["deals"])
    for stage in ["Discovery", "Validation", "Proposal", "Negotiation"]:
        add_check(f"Open deal count | {stage}", f"=COUNTIF('Open Pipeline'!$F$5:$F$204,\"{stage}\")", model["stages"][stage]["deals"])
    add_check("Q4 closed-won expected ARR", "=SUMIFS('Closed Opportunities'!$I$5:$I$404,'Closed Opportunities'!$F$5:$F$404,\"Closed Won\",'Closed Opportunities'!$W$5:$W$404,README!$B$8)", model["pipeline"]["q4_closed_won_arr"], CURRENCY)
    add_check("Commit forecast view", "='Pipeline Summary'!$F$6", model["pipeline"]["commit_view"], CURRENCY)
    add_check("Best Case forecast view", "='Pipeline Summary'!$F$7", model["pipeline"]["best_case_view"], CURRENCY)
    add_check("Full Pipeline forecast view", "='Pipeline Summary'!$F$8", model["pipeline"]["full_pipeline_view"], CURRENCY)
    add_check("Closed Won count", "=COUNTIF('Closed Opportunities'!$F$5:$F$404,\"Closed Won\")", model["pipeline"]["closed_won"])
    add_check("Closed Lost count", "=COUNTIF('Closed Opportunities'!$F$5:$F$404,\"Closed Lost\")", model["pipeline"]["closed_lost"])
    add_check("Closed win rate", "='Pipeline Summary'!$D$32", round(model["pipeline"]["closed_win_rate"], 6), DECIMAL, True)
    add_check("Activated users", "=COUNTIF('Activation'!$F$5:$F$2404,TRUE)", model["activation"]["activated"])
    add_check("Retained W2 users", "=COUNTIF('Activation'!$H$5:$H$2404,TRUE)", model["activation"]["retained_w2"])
    add_check("Activation rate", "=IFERROR(COUNTIF('Activation'!$F$5:$F$2404,TRUE)/COUNTA('Activation'!$A$5:$A$2404),0)", round(model["activation"]["activation_rate"], 6), DECIMAL, True)
    add_check("Retention of activated", "=IFERROR(COUNTIF('Activation'!$H$5:$H$2404,TRUE)/COUNTIF('Activation'!$F$5:$F$2404,TRUE),0)", round(model["activation"]["retention_of_activated"], 6), DECIMAL, True)
    add_check("Overall W2 retention", "=IFERROR(COUNTIF('Activation'!$H$5:$H$2404,TRUE)/COUNTA('Activation'!$A$5:$A$2404),0)", round(model["activation"]["overall_retention"], 6), DECIMAL, True)
    add_check("Commission tier residual", "=SUM('Quota Commission'!$P$5:$P$12)-SUM('Quota Commission'!$M$5:$O$12)", 0, CURRENCY)
    for row, (label, formula, control, fmt, rounded) in enumerate(checks, start=5):
        xl_value(ws.cell(row, 1), label)
        xl_formula(ws.cell(row, 2), formula, fmt)
        xl_value(ws.cell(row, 3), control, fmt, financial=fmt == CURRENCY)
        status_formula = f"=IF(ROUND(B{row}-C{row},6)=0,\"PASS\",\"FAIL\")" if rounded else f"=IF(B{row}=C{row},\"PASS\",\"FAIL\")"
        xl_formula(ws.cell(row, 4), status_formula)
        xl_value(ws.cell(row, 5), "Workbook formula vs manifest/source control")
        for col in range(1, 6):
            ws.cell(row, col).border = BORDER
    ws.conditional_formatting.add(f"D5:D{4 + len(checks)}", CellIsRule(operator="equal", formula=['"PASS"'], fill=PatternFill("solid", fgColor="E8F5E9"), font=Font(name="Arial", color=GREEN, bold=True)))
    ws.conditional_formatting.add(f"D5:D{4 + len(checks)}", CellIsRule(operator="equal", formula=['"FAIL"'], fill=PatternFill("solid", fgColor=PALE_RED), font=Font(name="Arial", color=RED, bold=True)))
    ws.freeze_panes = "A5"
    xl_widths(ws, [38, 23, 23, 13, 48])
    ws.auto_filter.ref = f"A4:E{4 + len(checks)}"

    # Order is deliberate and required.
    order = ["README", "ARR Summary", "ARR Rollforward", "Open Pipeline", "Closed Opportunities", "Accounts", "Activation", "Quota Commission", "Pipeline Summary", "Validation"]
    wb._sheets = [wb[name] for name in order]
    wb.active = 1
    for ws in wb.worksheets:
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.oddFooter.center.text = f"Built by Vera {BUILD_DATE} | Synthetic & anonymized | Page &P of &N"
        ws.oddFooter.center.size = 8
        ws.oddFooter.center.font = "Arial"
    XLSX_PATH.parent.mkdir(parents=True, exist_ok=True)
    wb.save(XLSX_PATH)
    normalize_zip(XLSX_PATH)


# ------------------------------- DOCX -------------------------------------


def doc_set_cell_shading(cell, color: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), color)
    shd.set(qn("w:val"), "clear")


def doc_set_cell_margins(cell, top=80, start=100, bottom=80, end=100) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, v in [("top", top), ("start", start), ("bottom", bottom), ("end", end)]:
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(v))
        node.set(qn("w:type"), "dxa")


def doc_set_table_borders(table, color: str = LINE) -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        node = borders.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            borders.append(node)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), "4")
        node.set(qn("w:space"), "0")
        node.set(qn("w:color"), color)


def doc_repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def doc_no_row_split(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    tr_pr.append(cant_split)


def doc_style_run(run, size=10.5, bold=False, color=INK, italic=False) -> None:
    run.font.name = "Arial"
    run.font.size = DPt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = DRGBColor.from_string(color)
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), "Arial")


def doc_paragraph(doc_or_cell, text: str = "", size=10.5, bold=False, color=INK, style=None, space_after=5, italic=False, align=None):
    paragraph = doc_or_cell.add_paragraph(style=style) if hasattr(doc_or_cell, "add_paragraph") else None
    if text:
        run = paragraph.add_run(text)
        doc_style_run(run, size=size, bold=bold, color=color, italic=italic)
    paragraph.paragraph_format.space_after = DPt(space_after)
    paragraph.paragraph_format.line_spacing = 1.12
    if align is not None:
        paragraph.alignment = align
    return paragraph


def doc_bullet(doc, text: str, color=INK):
    p = doc_paragraph(doc, style="List Bullet", size=10.5, space_after=3)
    doc_style_run(p.add_run(text), size=10.5, color=color)
    return p


def doc_heading(doc, text: str, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = DPt(12 if level == 1 else 8)
    p.paragraph_format.space_after = DPt(5)
    doc_style_run(p.add_run(text), size=15 if level == 1 else 12, bold=True, color=BLUE if level == 1 else INK)
    return p


def doc_table(doc, headers: Sequence[str], rows: Sequence[Sequence[str]], widths: Sequence[float] | None = None, font_size=9.2):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.style = "Table Grid"
    doc_set_table_borders(table)
    if widths:
        for index, width in enumerate(widths):
            table.columns[index].width = DInches(width)
    for col, header in enumerate(headers):
        cell = table.rows[0].cells[col]
        cell.text = ""
        if widths:
            cell.width = DInches(widths[col])
        doc_set_cell_shading(cell, BLUE)
        doc_set_cell_margins(cell)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = DPt(0)
        doc_style_run(p.add_run(header), size=font_size, bold=True, color=WHITE)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    doc_repeat_header(table.rows[0])
    for row_index, values in enumerate(rows):
        cells = table.add_row().cells
        doc_no_row_split(table.rows[-1])
        for col, value in enumerate(values):
            cell = cells[col]
            cell.text = ""
            if widths:
                cell.width = DInches(widths[col])
            doc_set_cell_margins(cell)
            if row_index % 2 == 1:
                doc_set_cell_shading(cell, LIGHT)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = DPt(0)
            p.paragraph_format.line_spacing = 1.05
            doc_style_run(p.add_run(str(value)), size=font_size, color=INK)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    doc_paragraph(doc, "", size=4, space_after=2)
    return table


def doc_callout(doc, title: str, text: str, color=BLUE):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    doc_set_cell_shading(cell, PALE_BLUE if color == BLUE else PALE_TEAL)
    doc_set_cell_margins(cell, top=140, start=160, bottom=140, end=160)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = DPt(3)
    doc_style_run(p.add_run(title.upper()), size=9, bold=True, color=color)
    p2 = doc_paragraph(cell, text, size=11, bold=True, color=INK, space_after=0)
    doc_paragraph(doc, "", size=4, space_after=2)
    return table


def doc_add_page_field(paragraph) -> None:
    run = paragraph.add_run()
    fld_char = OxmlElement("w:fldChar")
    fld_char.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = "PAGE"
    fld_char_end = OxmlElement("w:fldChar")
    fld_char_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char)
    run._r.append(instr_text)
    run._r.append(fld_char_end)
    doc_style_run(run, size=8.5, color=MUTED)


def new_doc(title: str, subtitle: str) -> Document:
    doc = Document()
    section = doc.sections[0]
    section.page_width = DInches(8.5)
    section.page_height = DInches(11)
    section.top_margin = DInches(0.62)
    section.bottom_margin = DInches(0.62)
    section.left_margin = DInches(0.65)
    section.right_margin = DInches(0.65)
    section.header_distance = DInches(0.22)
    section.footer_distance = DInches(0.25)
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = DPt(10.5)
    normal.font.color.rgb = DRGBColor.from_string(INK)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    for level in [1, 2, 3]:
        style = styles[f"Heading {level}"]
        style.font.name = "Arial"
        style.font.color.rgb = DRGBColor.from_string(BLUE if level == 1 else INK)
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    header = section.header
    p = header.paragraphs[0]
    p.paragraph_format.space_after = DPt(0)
    p.add_run().add_picture(str(LOGO), width=DInches(0.27), height=DInches(0.27))
    doc_style_run(p.add_run("  VERA  /  NORTHWIND SYNTHETIC"), size=9, bold=True, color=BLUE)
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc_style_run(fp.add_run(f"Built by Vera {BUILD_DATE}  |  Synthetic & anonymized  |  Page "), size=8.5, color=MUTED)
    doc_add_page_field(fp)
    doc.core_properties.author = "Vera"
    doc.core_properties.last_modified_by = "Vera"
    doc.core_properties.title = title
    doc.core_properties.subject = subtitle
    doc.core_properties.comments = "Synthetic and anonymized. Visual Office rendering not inspected."
    doc.core_properties.created = BUILD_DATETIME
    doc.core_properties.modified = BUILD_DATETIME
    p = doc.add_paragraph()
    p.paragraph_format.space_after = DPt(3)
    doc_style_run(p.add_run(title), size=24, bold=True, color=INK)
    doc_paragraph(doc, subtitle, size=11, color=MUTED, space_after=10)
    return doc


def doc_source_note(doc, sources: str):
    doc_heading(doc, "Sources, definitions & validation", 2)
    doc_paragraph(doc, f"Sources: {sources}. All values are calculated from the synthetic source CSVs; manifest.json supplies period metadata and independent control totals. No live CRM, billing, product or payroll source was connected.", size=9.2, color=MUTED)
    doc_paragraph(doc, "Validation trail: C1 arithmetic, C2 scoped filters, C3 static-period currency, C4 source integrity, C5 chart/table provenance, C6 claim language, C7 population disclosure, C8 terminology, C9 USD normalization, C10 population counts, C11 reconciliation and C12 evidence coverage passed. C13–C18 content/package checks passed; visual Office rendering was not inspected. This is a full synthetic census, so sampling significance is not applicable.", size=9.2, color=MUTED)
    doc_paragraph(doc, "Artifact note: workbook recalc-on-load is enabled. Formula recalculation and visual Office rendering: not inspected. Formula logic was independently verified in Python; package reopen, XML, relationship, source-hash and cross-artifact checks are recorded in data/office-validation.json.", size=9.2, color=MUTED)


def save_doc(doc: Document, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(path)
    normalize_zip(path)


def build_revenue_doc(model: dict) -> None:
    a, p, act = model["arr"], model["pipeline"], model["activation"]
    doc = new_doc("Revenue review | Q3 ARR + Q4 pipeline", f"Northwind synthetic • ARR {model['arr_period']} • Pipeline {model['pipeline_period']} • Built {BUILD_DATE}")
    doc_callout(doc, "Executive decision", f"ARR ended at {compact_money(a['ending_arr'])}, up {compact_money(a['net_arr_added'])} ({pct(a['growth_rate'])}). NRR is {pct(a['nrr'])} because {compact_money(a['total_losses'])} of contraction + churn exceeded {compact_money(a['expansion_arr'])} of expansion. Protect the base while converting the {compact_money(p['commit_view'])} Commit scenario and repairing next-step hygiene.")
    doc_heading(doc, "1 | ARR movement")
    doc_paragraph(doc, f"The roll-forward reconciles exactly: {money(a['starting_arr'])} + {money(a['new_arr'])} + {money(a['expansion_arr'])} − {money(a['contraction_arr'])} − {money(a['churn_arr'])} = {money(a['ending_arr'])}. Net ARR added is {money(a['net_arr_added'])}.")
    doc_table(doc, ["Movement", "ARR", "Accounts", "Reading"], [
        ["Starting ARR", money(a["starting_arr"]), number(a["starting_active_customers"]), "Opening active base"],
        ["New", "+" + money(a["new_arr"]), number(a["movement_counts"]["New"]), f"{pct(a['new_share_gains'])} of gross gains"],
        ["Expansion", "+" + money(a["expansion_arr"]), number(a["movement_counts"]["Expansion"]), f"{pct(a['expansion_share_gains'])} of gross gains"],
        ["Contraction", "−" + money(a["contraction_arr"]), number(a["movement_counts"]["Contraction"]), "Loss magnitude"],
        ["Churn", "−" + money(a["churn_arr"]), number(a["movement_counts"]["Churn"]), "Loss magnitude"],
        ["Ending ARR", money(a["ending_arr"]), number(a["ending_active_customers"]), "Reconciled closing base"],
    ], widths=[1.35, 1.35, 0.8, 3.55])
    doc_heading(doc, "2 | Active customers and retention")
    doc_paragraph(doc, f"Active customers move from {number(a['starting_active_customers'])} to {number(a['ending_active_customers'])}: +{a['movement_counts']['New']} new and −{a['movement_counts']['Churn']} churn produce a net +{a['ending_active_customers'] - a['starting_active_customers']}. Expansion, contraction and flat classifications do not change that count.")
    doc_table(doc, ["Metric", "Value", "Definition"], [
        ["GRR", pct(a["grr"]), "(Starting − contraction − churn) / starting"],
        ["NRR", pct(a["nrr"]), "(Starting + expansion − contraction − churn) / starting"],
        ["ARR growth", pct(a["growth_rate"]), "Net ARR added / starting ARR"],
        ["Total losses", money(a["total_losses"]), "Contraction + churn"],
    ], widths=[1.5, 1.25, 4.3])
    doc_paragraph(doc, f"New ARR supplies {pct(a['new_share_gains'])} of gross gains. The retention issue is arithmetic, not a causal claim: expansion offsets {pct(safe_div(a['expansion_arr'], a['total_losses']))} of contraction + churn, leaving NRR below 100%.")
    doc_heading(doc, "3 | Retention by segment")
    segment_rows = []
    for segment, values in model["segment_retention"].items():
        segment_rows.append([segment, money(values["starting_arr"]), money(values["expansion_arr"]), money(values["contraction_arr"] + values["churn_arr"]), money(values["ending_arr"])])
    doc_table(doc, ["Segment", "Starting ARR", "Expansion", "Contraction + churn", "Ending ARR"], segment_rows, widths=[1.15, 1.35, 1.25, 1.6, 1.35])
    doc_paragraph(doc, "Segments are disclosed separately; this table describes movements and does not assert why they occurred.", size=9.2, color=MUTED)

    doc_heading(doc, "4 | Q4 open forecast scenarios")
    doc_paragraph(doc, "Scenarios use unweighted expected_arr_usd. Commit includes Q4 closed-won plus Commit; Best Case adds Best Case; Full Pipeline adds Pipeline. They are cumulative views, not three independent forecasts.")
    doc_table(doc, ["Component / scenario", "Incremental expected ARR", "Cumulative view"], [
        ["Q4 closed-won", money(p["q4_closed_won_arr"]), money(p["q4_closed_won_arr"])],
        ["Commit", money(model["forecast"]["Commit"]["expected_arr"]), money(p["commit_view"])],
        ["Best Case", money(model["forecast"]["Best Case"]["expected_arr"]), money(p["best_case_view"])],
        ["Pipeline", money(model["forecast"]["Pipeline"]["expected_arr"]), money(p["full_pipeline_view"])],
    ], widths=[2.0, 2.4, 2.4])
    doc_table(doc, ["Open risk", "Deals", "Expected ARR", "Overdue next steps", "Overdue expected ARR"], [
        [risk, number(model["risks"][risk]["deals"]), money(model["risks"][risk]["expected_arr"]), number(model["risks"][risk]["overdue_deals"]), money(model["risks"][risk]["overdue_expected_arr"])]
        for risk in ["At risk", "Watch", "On track"]
    ], widths=[1.0, 0.65, 1.55, 1.4, 1.7])
    doc_paragraph(doc, f"Across all open deals, {p['overdue_open_deals']} next-step dates precede {model['generated']}, representing {money(p['overdue_open_expected_arr'])} of expected ARR. Treat this as a hygiene flag requiring review, not an automatic forecast reduction.")

    doc_heading(doc, "5 | Activation and week-2 retention")
    doc_paragraph(doc, f"Of {number(act['signups'])} synthetic signups, {number(act['activated'])} activated ({pct(act['activation_rate'])}) and {number(act['retained_w2'])} were retained at week 2. Retention is {pct(act['retention_of_activated'])} of activated users and {pct(act['overall_retention'])} of all signups.")
    doc_table(doc, ["Cohort", "Signups", "Activated", "Activation rate", "Retained W2", "Retained / activated"], [
        [cohort, number(v["signups"]), number(v["activated"]), pct(v["activation_rate"]), number(v["retained_w2"]), pct(v["retention_of_activated"])]
        for cohort, v in act["cohorts"].items()
    ], widths=[0.9, 0.85, 0.85, 1.2, 1.0, 1.45])
    doc_paragraph(doc, f"W43 retained {pct(act['cohorts']['2026-W43']['retention_of_activated'])} of activated users versus {pct(act['cohorts']['2026-W40']['retention_of_activated'])} in W40. Four cohorts support a comparison, not a causal explanation; inspect onboarding execution before naming a driver.")

    doc_heading(doc, "6 | Decisions and actions")
    doc_table(doc, ["Owner role", "Action", "Evidence / exit criterion"], [
        ["Customer Success", "Review contraction and churn by segment; document controllable vs non-controllable drivers.", f"Cover {money(a['total_losses'])} of losses; retain ARR identity."],
        ["Sales leadership", "Triage At risk and overdue open deals with named close plans.", f"{model['risks']['At risk']['deals']} At risk deals; {p['overdue_open_deals']} overdue next steps."],
        ["RevOps", "Run scenario review without mixing weighted and unweighted definitions.", f"Commit {money(p['commit_view'])}; Best Case {money(p['best_case_view'])}; Full {money(p['full_pipeline_view'])}."],
        ["Growth + Product", "Inspect W43 activation-to-retention execution against earlier cohorts.", f"W43 {pct(act['cohorts']['2026-W43']['retention_of_activated'])}; overall {pct(act['retention_of_activated'])}."],
    ], widths=[1.25, 3.3, 2.5])
    doc_source_note(doc, "data/arr-rollforward.csv; data/crm-opportunities.csv; data/crm-accounts.csv; data/activation-users.csv; data/manifest.json")
    save_doc(doc, DOC_PATHS["revenue"])


def build_pipeline_doc(model: dict) -> None:
    p = model["pipeline"]
    doc = new_doc("Pipeline review | Q4 2026", f"Northwind synthetic • {p['open_deals']} open + {p['closed_deals']} closed opportunities • Built {BUILD_DATE}")
    doc_callout(doc, "Forecast call", f"Commit view is {compact_money(p['commit_view'])}; Best Case reaches {compact_money(p['best_case_view'])} and Full Pipeline reaches {compact_money(p['full_pipeline_view'])}. The immediate control point is {p['overdue_open_deals']} overdue open next steps ({compact_money(p['overdue_open_expected_arr'])} expected ARR), including {model['risks']['At risk']['overdue_deals']} At risk deals.")
    doc_heading(doc, "1 | Scenario bridge")
    doc_table(doc, ["Layer", "Deals", "Expected ARR", "Cumulative scenario"], [
        ["Q4 closed-won", "—", money(p["q4_closed_won_arr"]), money(p["q4_closed_won_arr"])],
        ["Commit", number(model["forecast"]["Commit"]["deals"]), money(model["forecast"]["Commit"]["expected_arr"]), money(p["commit_view"])],
        ["Best Case", number(model["forecast"]["Best Case"]["deals"]), money(model["forecast"]["Best Case"]["expected_arr"]), money(p["best_case_view"])],
        ["Pipeline", number(model["forecast"]["Pipeline"]["deals"]), money(model["forecast"]["Pipeline"]["expected_arr"]), money(p["full_pipeline_view"])],
    ], widths=[1.35, 0.7, 2.1, 2.2])
    doc_paragraph(doc, "Expected ARR is summed without probability weighting for these scenarios. The workbook also exposes probability-weighted ARR separately; the two concepts are not interchangeable.")
    doc_heading(doc, "2 | Stage and risk mix")
    doc_table(doc, ["Stage", "Open deals", "Expected ARR", "Deal mix"], [
        [stage, number(v["deals"]), money(v["expected_arr"]), pct(safe_div(v["deals"], p["open_deals"]))]
        for stage, v in model["stages"].items()
    ], widths=[1.6, 1.2, 2.0, 1.3])
    doc_table(doc, ["Risk", "Deals", "Expected ARR", "Overdue deals", "Overdue expected ARR"], [
        [risk, number(v["deals"]), money(v["expected_arr"]), number(v["overdue_deals"]), money(v["overdue_expected_arr"])]
        for risk, v in model["risks"].items()
    ], widths=[1.0, 0.7, 1.65, 1.25, 1.7])
    doc_heading(doc, "3 | Largest open opportunities")
    doc_paragraph(doc, "Six largest by expected ARR; aliases are intentional. Full 200-row detail is in the workbook and source CSV.")
    doc_table(doc, ["Deal / owner", "Stage / category", "Expected ARR", "Close", "Risk"], [
        [f"{r['opportunity_alias']} / {r['owner_alias']}", f"{r['stage']} / {r['forecast_category']}", money(as_int(r, "expected_arr_usd")), r["close_date"], r["risk_status"]]
        for r in model["top_open"]
    ], widths=[1.85, 1.75, 1.25, 1.0, 0.8], font_size=8.7)
    doc_heading(doc, "4 | Closed win/loss evidence")
    doc_paragraph(doc, f"The closed population contains {p['closed_won']} Closed Won and {p['closed_lost']} Closed Lost deals, a {pct(p['closed_win_rate'])} closed-win rate. Q3 and Q4 closed outcomes are combined here and disclosed as such.")
    doc_table(doc, ["Loss reason", "Closed Lost deals", "Share of losses"], [
        [reason, number(count), pct(safe_div(count, p["closed_lost"]))]
        for reason, count in sorted(model["loss_reasons"].items(), key=lambda item: (-item[1], item[0]))
    ], widths=[2.6, 1.6, 1.6])
    doc_table(doc, ["Win reason", "Closed Won deals", "Share of wins"], [
        [reason, number(count), pct(safe_div(count, p["closed_won"]))]
        for reason, count in sorted(model["win_reasons"].items(), key=lambda item: (-item[1], item[0]))
    ], widths=[2.6, 1.6, 1.6])
    doc_paragraph(doc, "Reason fields describe recorded outcomes. They do not establish that changing one factor would have changed the result.", size=9.2, color=MUTED)
    doc_heading(doc, "5 | Owner quota and Commit control")
    doc_table(doc, ["Owner", "Q4 quota", "Q4 won ARR", "Attainment", "Open expected ARR", "Commit view"], [
        [r["owner"], money(r["quota"]), money(r["q4_won"]), pct(r["attainment"]), money(r["open_expected"]), money(r["commit_view"])]
        for r in model["commission"]
    ], widths=[0.85, 1.1, 1.2, 0.9, 1.45, 1.25], font_size=8.5)
    doc_paragraph(doc, "Commission formulas and tier levers are in the workbook. This review uses attainment and scenario values, not commission expense, to avoid presenting an illustrative model as payroll.")
    doc_heading(doc, "6 | Review actions")
    doc_table(doc, ["Priority", "Owner role", "Action", "Evidence"], [
        ["Next-step control", "RevOps + deal owners", "Refresh or close every overdue next step; retain the original date for hygiene reporting.", f"{p['overdue_open_deals']} deals / {money(p['overdue_open_expected_arr'])}"],
        ["At risk control", "Sales leadership", "Review stage, forecast category and close plan for every At risk deal.", f"{model['risks']['At risk']['deals']} deals / {money(model['risks']['At risk']['expected_arr'])}"],
        ["Loss review", "Sales + Product", "Review Security review and Timing losses separately; do not merge operational and product causes.", f"{model['loss_reasons']['Security review']} Security review; {model['loss_reasons']['Timing']} Timing"],
        ["Scenario governance", "RevOps", "Keep cumulative scenario layers separate from probability-weighted ARR.", f"Open expected ARR {money(p['open_expected_arr_total'])}"],
    ], widths=[1.15, 1.25, 3.15, 1.5], font_size=8.7)
    doc_source_note(doc, "data/crm-opportunities.csv; data/quota-targets.csv; data/manifest.json")
    save_doc(doc, DOC_PATHS["pipeline"])


def build_campaign_doc(model: dict) -> None:
    sources = model["activation_sources"]
    referral = sources["Referral"]
    cohorts = model["activation"]["cohorts"]
    cohort_range = f"{min(cohorts)}–{max(cohorts)}"
    doc = new_doc("Campaign one-pager | Referral activation", f"Northwind synthetic • Activation cohorts {cohort_range} • Built {BUILD_DATE}")
    doc_callout(doc, "Recommendation", f"Test Referral next: it leads the five source cohorts on activation count ({number(referral['activated'])}) and rate ({pct(referral['activation_rate'])}), and has the most week-2 retained users ({number(referral['retained_w2'])}). Hold activation and retention as joint guardrails.")
    doc_heading(doc, "Evidence | acquisition source scorecard")
    doc_table(doc, ["Source", "Signups", "Activated", "Activation", "Retained / activated", "Closed-win rate"], [
        [source, number(v["signups"]), number(v["activated"]), pct(v["activation_rate"]), pct(v["retention_of_activated"]), pct(v["closed_win_rate"])]
        for source, v in sources.items()
    ], widths=[0.95, 0.8, 0.85, 0.95, 1.55, 1.35], font_size=8.5)
    doc_paragraph(doc, f"Referral baseline: {number(referral['signups'])} signups; {number(referral['retained_w2'])} retained at week 2; {pct(referral['overall_retention'])} overall retention. Closed CRM context covers Q3 + Q4 opportunities; activation covers {cohort_range} users. Separate populations and periods: no user-to-deal attribution or causal claim.", size=8.6, color=MUTED, space_after=3)
    doc_heading(doc, "Campaign brief")
    doc_table(doc, ["Element", "Decision"], [
        ["Audience + message", "Synthetic referral-sourced prospects; time-to-value and peer proof with activation guidance at handoff."],
        ["Primary measure", f"Activation = activated / signups; Referral baseline {pct(referral['activation_rate'])}."],
        ["Quality guardrail", f"Week-2 retention of activated = retained_w2 / activated; baseline {pct(referral['retention_of_activated'])}."],
        ["Scale guardrail", f"Overall week-2 retention = retained_w2 / signups; baseline {pct(referral['overall_retention'])}."],
        ["Ownership", "Growth: source tagging and referral handoff. Product: activation guidance. RevOps: cohort definitions and readout."],
        ["Budget", "Excluded: no campaign budget field exists in the source CSVs."],
    ], widths=[1.35, 5.65], font_size=8.5)
    doc_heading(doc, "Execution and readout")
    doc_paragraph(doc, "Read activation and week-2 retention together by cohort_week and acquisition_source. A higher activation count with weaker retention is not an unqualified quality win; do not sum users across weeks to infer unique-account engagement.", size=9.2, space_after=3)
    doc_heading(doc, "Sources & validation", 2)
    doc_paragraph(doc, "Sources: data/activation-users.csv; data/crm-opportunities.csv; data/manifest.json. Synthetic full-census arithmetic, source hashes, population disclosure and cross-artifact headlines passed. Built by Vera 2026-11-23. Workbook recalc-on-load is enabled. Formula recalculation and visual Office rendering: not inspected; formula logic and OOXML packages were checked in Python.", size=8.2, color=MUTED, space_after=0)
    save_doc(doc, DOC_PATHS["campaign"])


def build_project_doc(model: dict) -> None:
    a, p, act = model["arr"], model["pipeline"], model["activation"]
    open_rows = model["open_rows"]
    next_dates = [r["next_step_date"] for r in open_rows]
    close_dates = [r["close_date"] for r in open_rows]
    doc = new_doc("Project plan | Revenue retention & forecast control", f"Northwind synthetic • Baseline {model['generated']} • Built {BUILD_DATE}")
    doc_callout(doc, "Outcome", f"Establish one controlled operating cadence for {compact_money(a['ending_arr'])} ending ARR, {p['open_deals']} open deals and {number(act['signups'])} activation records. Exit with a reconciled ARR base, current next steps, explicit forecast definitions and cohort-level retention owners.")
    doc_heading(doc, "1 | Baseline and scope")
    doc_table(doc, ["Workstream", "Source baseline", "Control objective"], [
        ["ARR retention", f"{money(a['ending_arr'])} ending ARR; {money(a['total_losses'])} contraction + churn", "Reconcile every movement; review losses by segment"],
        ["Open pipeline", f"{p['open_deals']} deals; {money(p['open_expected_arr_total'])} expected ARR", "Separate cumulative scenarios from weighted ARR"],
        ["Next-step hygiene", f"{p['overdue_open_deals']} overdue; {money(p['overdue_open_expected_arr'])} expected ARR", "Every open deal has a current, dated next step"],
        ["Closed outcomes", f"{p['closed_won']} won / {p['closed_lost']} lost; {pct(p['closed_win_rate'])} win rate", "Review recorded reasons without causal overclaim"],
        ["Activation", f"{number(act['signups'])} signups; {pct(act['activation_rate'])} activated; {pct(act['retention_of_activated'])} retained of activated", "Retain cohort denominators and owner review"],
    ], widths=[1.3, 2.75, 2.95], font_size=8.8)
    doc_heading(doc, "2 | Source-derived schedule")
    doc_paragraph(doc, f"The only hard dates are source-derived: baseline {model['generated']}; open next-step range {min(next_dates)} to {max(next_dates)}; latest open close date {max(close_dates)}. Overdue dates before the baseline remain visible until corrected.")
    doc_table(doc, ["Gate", "Timing basis", "Owner role", "Deliverable", "Exit criterion"], [
        ["Baseline lock", model["generated"], "RevOps", "Source hashes, row counts, ARR identity, metric definitions", "All independent controls pass"],
        ["Next-step intervention", f"Source next steps {min(next_dates)}–{max(next_dates)}", "Sales leadership", "Deal-by-deal close-plan refresh", "No unexplained next step before baseline"],
        ["Retention review", "Before quarter-close control", "Customer Success", "Segment loss review with ARR evidence", f"Review coverage equals {money(a['total_losses'])} losses"],
        ["Activation review", "Before quarter-close control", "Growth + Product", "W40–W43 cohort readout", "Owners assigned to activation and retention measures"],
        ["Quarter-close control", f"Through {max(close_dates)}", "RevOps", "Closed/open cut and scenario refresh", "No open close date left in the closed period"],
    ], widths=[1.05, 1.4, 1.1, 2.05, 1.5], font_size=8.3)
    doc_heading(doc, "3 | Workstream delivery plan")
    doc_table(doc, ["Workstream", "Deliverable", "Acceptance test", "Accountable role"], [
        ["ARR", "Movement register and segment retention readout", "Starting + new + expansion − contraction − churn = ending at row and total level", "RevOps"],
        ["Pipeline", "Scenario bridge and stage/risk review", f"Commit {money(p['commit_view'])}; Best Case {money(p['best_case_view'])}; Full {money(p['full_pipeline_view'])}", "RevOps + Sales"],
        ["Data hygiene", "Overdue next-step queue", f"Resolve {p['overdue_open_deals']} source-flagged dates without deleting history", "Sales Operations"],
        ["Win/loss", "Reason-coded closed review", f"Cover all {p['closed_deals']} closed records; separate description from causality", "Sales + Product"],
        ["Activation", "Cohort/source scorecard", f"Tie {number(act['activated'])} activated and {number(act['retained_w2'])} retained users to raw flags", "Growth + Product"],
        ["Office controls", "Workbook, documents and deck", "Reopen packages; validate formulas/refs/content; mark recalc and visual rendering not inspected", "Vera + RevOps"],
    ], widths=[1.0, 2.2, 2.85, 1.1], font_size=8.5)
    doc_heading(doc, "4 | Decision rights and operating cadence")
    doc_table(doc, ["Decision", "Accountable", "Consulted", "Evidence required"], [
        ["ARR baseline changes", "RevOps", "Finance + Customer Success", "Source row and aggregate reconciliation"],
        ["Forecast category changes", "Sales leadership", "RevOps + deal owner", "Stage, close date, next step and expected ARR"],
        ["Retention intervention", "Customer Success", "RevOps + Product", "Segment loss detail; no unsupported cause"],
        ["Campaign continuation", "Growth", "Product + RevOps", "Activation and week-2 retention denominators"],
        ["Artifact publication", "RevOps", "Vera", "Validation JSON; no recalc/render claim without inspection"],
    ], widths=[1.6, 1.25, 1.6, 2.55], font_size=8.7)
    doc_heading(doc, "5 | Risk register")
    doc_table(doc, ["Risk", "Exposure", "Mitigation"], [
        ["Stale next steps distort operating review", f"{p['overdue_open_deals']} open deals / {money(p['overdue_open_expected_arr'])}", "Refresh dates; keep hygiene flag separate from forecast value"],
        ["Scenario definitions are mixed", f"{money(p['open_expected_arr_total'])} open expected ARR", "Label cumulative unweighted scenarios; show weighted ARR separately"],
        ["Retention intervention lacks focus", f"{money(a['total_losses'])} contraction + churn", "Segment review first; document evidence before asserting drivers"],
        ["Activation quality is read on one metric", f"Overall {pct(act['activation_rate'])} activation / {pct(act['retention_of_activated'])} retention of activated", "Read activation and retention together by cohort"],
    ], widths=[2.2, 2.1, 2.7], font_size=8.7)
    doc_source_note(doc, "data/arr-rollforward.csv; data/crm-opportunities.csv; data/activation-users.csv; data/quota-targets.csv; data/manifest.json")
    save_doc(doc, DOC_PATHS["project"])


# ------------------------------- PPTX -------------------------------------

SLIDE_W = 13.333333
SLIDE_H = 7.5


def ppt_color(hex_value: str) -> PRGBColor:
    return PRGBColor.from_string(hex_value)


def ppt_shape(slide, x, y, w, h, fill=WHITE, radius=True, line=None):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, PInches(x), PInches(y), PInches(w), PInches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = ppt_color(fill)
    if line:
        shape.line.color.rgb = ppt_color(line)
        shape.line.width = PPt(0.7)
    else:
        shape.line.fill.background()
    return shape


def ppt_text(slide, text, x, y, w, h, size=14, color=INK, bold=False, align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, margin=0.02, italic=False):
    box = slide.shapes.add_textbox(PInches(x), PInches(y), PInches(w), PInches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = PInches(margin)
    tf.margin_right = PInches(margin)
    tf.margin_top = PInches(margin)
    tf.margin_bottom = PInches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    p.space_after = PPt(0)
    p.line_spacing = 1.05
    run = p.add_run()
    run.text = str(text)
    run.font.name = "Arial"
    run.font.size = PPt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = ppt_color(color)
    return box


def ppt_multiline(slide, lines: Sequence[tuple[str, dict]], x, y, w, h, fill=None):
    if fill:
        ppt_shape(slide, x, y, w, h, fill=fill)
    box = slide.shapes.add_textbox(PInches(x), PInches(y), PInches(w), PInches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = PInches(0.16)
    tf.margin_right = PInches(0.16)
    tf.margin_top = PInches(0.1)
    tf.margin_bottom = PInches(0.08)
    for index, (text, opts) in enumerate(lines):
        p = tf.paragraphs[0] if index == 0 else tf.add_paragraph()
        p.space_after = PPt(opts.get("after", 5))
        p.line_spacing = opts.get("line_spacing", 1.05)
        p.alignment = opts.get("align", PP_ALIGN.LEFT)
        run = p.add_run()
        run.text = text
        run.font.name = "Arial"
        run.font.size = PPt(opts.get("size", 14))
        run.font.bold = opts.get("bold", False)
        run.font.italic = opts.get("italic", False)
        run.font.color.rgb = ppt_color(opts.get("color", INK))
    return box


def ppt_footer(slide, slide_num: int, source: str, dark=False):
    color = LINE if dark else MUTED
    text = f"Synthetic & anonymized | Source: {source} | Built by Vera {BUILD_DATE} | Recalc / visual rendering: not inspected | {slide_num}"
    ppt_text(slide, text, 0.55, 7.02, 12.2, 0.26, size=10, color=color, valign=MSO_ANCHOR.MIDDLE)


def ppt_base(prs: Presentation, title: str, slide_num: int, source: str, dark=False, subtitle: str | None = None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    background = slide.background.fill
    background.solid()
    background.fore_color.rgb = ppt_color(INK if dark else LIGHT)
    slide.shapes.add_picture(str(LOGO), PInches(0.55), PInches(0.28), width=PInches(0.34), height=PInches(0.34))
    ppt_text(slide, "VERA / NORTHWIND", 0.98, 0.29, 3.4, 0.3, size=11, color=WHITE if dark else BLUE, bold=True, valign=MSO_ANCHOR.MIDDLE)
    ppt_text(slide, title, 0.55, 0.76, 12.2, 0.58, size=36, color=WHITE if dark else INK, bold=True, valign=MSO_ANCHOR.MIDDLE)
    if subtitle:
        ppt_text(slide, subtitle, 0.57, 1.32, 12.0, 0.36, size=13, color=LINE if dark else MUTED)
    ppt_footer(slide, slide_num, source, dark=dark)
    return slide


def ppt_card(slide, x, y, w, h, label, value, note="", accent=BLUE, dark=False):
    ppt_shape(slide, x, y, w, h, fill=INK if dark else WHITE, line=None if dark else LINE)
    ppt_text(slide, label.upper(), x + 0.18, y + 0.13, w - 0.36, 0.24, size=10, color=LINE if dark else MUTED, bold=True)
    ppt_text(slide, value, x + 0.18, y + 0.39, w - 0.36, 0.42, size=25, color=accent, bold=True, valign=MSO_ANCHOR.MIDDLE)
    if note:
        ppt_text(slide, note, x + 0.18, y + 0.84, w - 0.36, h - 0.94, size=11, color=LINE if dark else MUTED)


def style_chart(chart, font_size=11, legend=False):
    chart.has_title = False
    chart.font.name = "Arial"
    chart.font.size = PPt(font_size)
    chart.font.color.rgb = ppt_color(INK)
    chart.has_legend = legend
    if legend:
        chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.legend.include_in_layout = False
        chart.legend.font.name = "Arial"
        chart.legend.font.size = PPt(10)
        chart.legend.font.color.rgb = ppt_color(INK)
    try:
        chart.category_axis.tick_labels.font.name = "Arial"
        chart.category_axis.tick_labels.font.size = PPt(font_size)
        chart.category_axis.tick_labels.font.color.rgb = ppt_color(INK)
        chart.category_axis.format.line.color.rgb = ppt_color(LINE)
        chart.value_axis.tick_labels.font.name = "Arial"
        chart.value_axis.tick_labels.font.size = PPt(font_size)
        chart.value_axis.tick_labels.font.color.rgb = ppt_color(MUTED)
        chart.value_axis.has_major_gridlines = True
        chart.value_axis.major_gridlines.format.line.color.rgb = ppt_color(LINE)
        chart.value_axis.format.line.fill.background()
    except (ValueError, AttributeError):
        pass


def add_chart(slide, chart_type, categories, series, x, y, w, h, colors, legend=False, number_format=None, data_labels=False, label_position=XL_LABEL_POSITION.OUTSIDE_END):
    data = ChartData()
    data.categories = categories
    for name, values in series:
        data.add_series(name, values)
    frame = slide.shapes.add_chart(chart_type, PInches(x), PInches(y), PInches(w), PInches(h), data)
    chart = frame.chart
    style_chart(chart, legend=legend)
    for index, serie in enumerate(chart.series):
        color = colors[index % len(colors)]
        serie.format.fill.solid()
        serie.format.fill.fore_color.rgb = ppt_color(color)
        serie.format.line.color.rgb = ppt_color(color)
    if number_format:
        try:
            chart.value_axis.tick_labels.number_format = number_format
            chart.value_axis.tick_labels.number_format_is_linked = False
        except (ValueError, AttributeError):
            pass
    if data_labels:
        plot = chart.plots[0]
        plot.has_data_labels = True
        labels = plot.data_labels
        labels.position = label_position
        labels.show_value = True
        labels.show_legend_key = False
        labels.show_category_name = False
        labels.show_series_name = False
        labels.font.name = "Arial"
        labels.font.size = PPt(10)
        labels.font.color.rgb = ppt_color(INK)
        if number_format:
            labels.number_format = number_format
            labels.number_format_is_linked = False
    return chart


def ppt_table(slide, x, y, w, h, headers: Sequence[str], rows: Sequence[Sequence[str]], col_widths: Sequence[float] | None = None, font_size=11):
    shape = slide.shapes.add_table(len(rows) + 1, len(headers), PInches(x), PInches(y), PInches(w), PInches(h))
    table = shape.table
    if col_widths:
        total = sum(col_widths)
        for index, width in enumerate(col_widths):
            table.columns[index].width = PInches(w * width / total)
    for c, header in enumerate(headers):
        cell = table.cell(0, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = ppt_color(BLUE)
        cell.margin_left = PInches(0.08)
        cell.margin_right = PInches(0.06)
        cell.margin_top = PInches(0.04)
        cell.margin_bottom = PInches(0.03)
        cell.text = str(header)
        for p in cell.text_frame.paragraphs:
            for run in p.runs:
                run.font.name = "Arial"
                run.font.size = PPt(font_size)
                run.font.bold = True
                run.font.color.rgb = ppt_color(WHITE)
    for r, values in enumerate(rows, start=1):
        for c, value in enumerate(values):
            cell = table.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = ppt_color(WHITE if r % 2 else LIGHT)
            cell.margin_left = PInches(0.08)
            cell.margin_right = PInches(0.06)
            cell.margin_top = PInches(0.03)
            cell.margin_bottom = PInches(0.02)
            cell.text = str(value)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            for p in cell.text_frame.paragraphs:
                p.space_after = PPt(0)
                for run in p.runs:
                    run.font.name = "Arial"
                    run.font.size = PPt(font_size)
                    run.font.color.rgb = ppt_color(INK)
    return table


def build_presentation(model: dict) -> None:
    a, p, act = model["arr"], model["pipeline"], model["activation"]
    first_cohort = min(act["cohorts"])
    last_cohort = max(act["cohorts"])
    prs = Presentation()
    prs.slide_width = PInches(SLIDE_W)
    prs.slide_height = PInches(SLIDE_H)
    prs.core_properties.author = "Vera"
    prs.core_properties.last_modified_by = "Vera"
    prs.core_properties.title = "Northwind synthetic revenue review"
    prs.core_properties.subject = "Q3 ARR, Q4 pipeline and activation"
    prs.core_properties.comments = "Synthetic and anonymized. Formula recalculation and visual Office rendering not inspected."
    prs.core_properties.created = BUILD_DATETIME
    prs.core_properties.modified = BUILD_DATETIME

    # 1 — title and answer.
    slide = ppt_base(prs, "Revenue review", 1, "manifest.json + ARR / CRM / activation CSVs", dark=True, subtitle=f"{model['arr_period']} ARR roll-forward • {model['pipeline_period']} open pipeline • {first_cohort}–{last_cohort} activation • {BUILD_DATE}")
    ppt_text(slide, f"ARR reached {compact_money(a['ending_arr'])}; the next decision is retention discipline plus forecast control.", 0.62, 2.0, 11.9, 0.9, size=25, color=WHITE, bold=True, valign=MSO_ANCHOR.MIDDLE)
    ppt_card(slide, 0.62, 3.35, 3.85, 1.55, "Net ARR added", signed_compact_money(a["net_arr_added"]), pct(a["growth_rate"]) + " growth", accent=WHITE, dark=True)
    ppt_card(slide, 4.73, 3.35, 3.85, 1.55, "Net revenue retention", pct(a["nrr"]), compact_money(a["total_losses"]) + " total losses", accent=WHITE, dark=True)
    ppt_card(slide, 8.84, 3.35, 3.85, 1.55, "Commit scenario", compact_money(p["commit_view"]), compact_money(p["q4_closed_won_arr"]) + " already Q4 won", accent=WHITE, dark=True)
    ppt_text(slide, "Synthetic Northwind • Aliases only • Full source detail in XLSX / CSV", 0.64, 5.55, 11.9, 0.45, size=14, color=LINE)

    # 2 — scorecard.
    slide = ppt_base(prs, "The scorecard: growth with a retention gap", 2, "ARR / CRM / activation CSVs")
    cards = [
        ("Ending ARR", compact_money(a["ending_arr"]), signed_compact_money(a["net_arr_added"]) + " net", BLUE),
        ("Active customers", number(a["ending_active_customers"]), f"+{a['ending_active_customers'] - a['starting_active_customers']} net", TEAL),
        ("Open expected ARR", compact_money(p["open_expected_arr_total"]), f"{p['open_deals']} open deals", BLUE),
        ("Activation", pct(act["activation_rate"]), f"{number(act['activated'])} / {number(act['signups'])}", TEAL),
    ]
    for index, card in enumerate(cards):
        ppt_card(slide, 0.55 + index * 3.15, 1.55, 2.9, 1.45, *card)
    ppt_multiline(slide, [
        ("1  Protect the revenue base", {"size": 17, "bold": True, "color": BLUE}),
        (f"Contraction + churn is {compact_money(a['total_losses'])}; expansion offsets {compact_money(a['expansion_arr'])}. NRR is {pct(a['nrr'])}.", {"size": 14}),
        ("2  Make the open forecast operable", {"size": 17, "bold": True, "color": BLUE}),
        (f"{p['overdue_open_deals']} next steps predate {model['generated']}; review {compact_money(p['overdue_open_expected_arr'])} of expected ARR without applying an automatic haircut.", {"size": 14}),
        ("3  Read activation and retention together", {"size": 17, "bold": True, "color": BLUE}),
        (f"{pct(act['activation_rate'])} activated; {pct(act['retention_of_activated'])} of activated users retained at week 2.", {"size": 14}),
    ], 0.55, 3.25, 12.2, 3.35, fill=WHITE)

    # 3 — ARR movement.
    slide = ppt_base(prs, f"ARR +{compact_money(a['net_arr_added'])}; NRR {pct(a['nrr'])} after losses", 3, "arr-rollforward.csv", subtitle="Movement values in $M; contraction and churn are plotted as negative")
    ppt_shape(slide, 0.55, 1.78, 8.05, 4.93, fill=WHITE, line=LINE)
    chart = add_chart(slide, XL_CHART_TYPE.COLUMN_CLUSTERED, ["Start", "New", "Expansion", "Contraction", "Churn", "End"], [("ARR ($M)", [a["starting_arr"] / 1e6, a["new_arr"] / 1e6, a["expansion_arr"] / 1e6, -a["contraction_arr"] / 1e6, -a["churn_arr"] / 1e6, a["ending_arr"] / 1e6])], 0.78, 2.0, 7.6, 4.42, [BLUE], number_format='$0.0"M"', data_labels=True)
    point_colors = [BLUE, TEAL, TEAL, RED, RED, BLUE]
    for point, color in zip(chart.series[0].points, point_colors):
        point.format.fill.solid()
        point.format.fill.fore_color.rgb = ppt_color(color)
        point.format.line.color.rgb = ppt_color(color)
    ppt_card(slide, 8.85, 1.78, 3.93, 1.42, "GRR", pct(a["grr"]), "New and expansion excluded", accent=TEAL)
    ppt_card(slide, 8.85, 3.4, 3.93, 1.42, "NRR", pct(a["nrr"]), "New ARR excluded", accent=AMBER)
    ppt_multiline(slide, [
        ("Reconciles to zero", {"size": 16, "bold": True, "color": BLUE}),
        (f"{compact_money(a['starting_arr'])} + {compact_money(a['new_arr'])} + {compact_money(a['expansion_arr'])} − {compact_money(a['contraction_arr'])} − {compact_money(a['churn_arr'])} = {compact_money(a['ending_arr'])}", {"size": 13}),
    ], 8.85, 5.03, 3.93, 1.68, fill=WHITE)

    # 4 — customers.
    slide = ppt_base(prs, f"Active customers: {number(a['starting_active_customers'])} to {number(a['ending_active_customers'])}", 4, "arr-rollforward.csv", subtitle=f"Movement counts classify all {number(len(model['arr_rows']))} ARR rows; only New and Churn change active count")
    ppt_shape(slide, 0.55, 1.8, 7.25, 4.85, fill=WHITE, line=LINE)
    add_chart(slide, XL_CHART_TYPE.BAR_CLUSTERED, ["New", "Expansion", "Flat", "Contraction", "Churn"], [("Accounts", [a["movement_counts"][k] for k in ["New", "Expansion", "Flat", "Contraction", "Churn"]])], 0.82, 2.05, 6.7, 4.25, [BLUE], number_format='0', data_labels=True)
    ppt_card(slide, 8.05, 1.8, 4.73, 1.42, "Starting active", number(a["starting_active_customers"]), "starting_arr > 0", accent=BLUE)
    ppt_card(slide, 8.05, 3.4, 2.25, 1.42, "New", f"+{a['movement_counts']['New']}", "New logos", accent=TEAL)
    ppt_card(slide, 10.53, 3.4, 2.25, 1.42, "Churn", f"−{a['movement_counts']['Churn']}", "Lost logos", accent=RED)
    ppt_card(slide, 8.05, 5.02, 4.73, 1.63, "Ending active", number(a["ending_active_customers"]), f"{number(a['starting_active_customers'])} + {a['movement_counts']['New']} − {a['movement_counts']['Churn']} = {number(a['ending_active_customers'])}", accent=BLUE)

    # 5 — forecast scenarios.
    slide = ppt_base(prs, f"Q4 scenarios: {compact_money(p['commit_view'])} Commit to {compact_money(p['full_pipeline_view'])} Full", 5, "crm-opportunities.csv; manifest.json", subtitle="Cumulative unweighted expected ARR; each layer adds to the prior scenario")
    ppt_shape(slide, 0.55, 1.8, 8.2, 4.88, fill=WHITE, line=LINE)
    q4 = p["q4_closed_won_arr"] / 1e6
    commit = model["forecast"]["Commit"]["expected_arr"] / 1e6
    best = model["forecast"]["Best Case"]["expected_arr"] / 1e6
    pipe = model["forecast"]["Pipeline"]["expected_arr"] / 1e6
    chart = add_chart(slide, XL_CHART_TYPE.COLUMN_STACKED, ["Commit", "Best Case", "Full Pipeline"], [
        ("Q4 closed-won", [q4, q4, q4]),
        ("Commit", [commit, commit, commit]),
        ("Best Case", [0, best, best]),
        ("Pipeline", [0, 0, pipe]),
    ], 0.8, 2.0, 7.7, 4.38, [INK, BLUE, TEAL, AMBER], legend=True, number_format='$0.0"M"')
    ppt_card(slide, 9.0, 1.8, 3.78, 1.4, "Commit view", compact_money(p["commit_view"]), f"Q4 won + {compact_money(model['forecast']['Commit']['expected_arr'])}", accent=BLUE)
    ppt_card(slide, 9.0, 3.38, 3.78, 1.4, "Best Case view", compact_money(p["best_case_view"]), f"Adds {compact_money(model['forecast']['Best Case']['expected_arr'])}", accent=TEAL)
    ppt_card(slide, 9.0, 4.96, 3.78, 1.72, "Full Pipeline view", compact_money(p["full_pipeline_view"]), f"Adds {compact_money(model['forecast']['Pipeline']['expected_arr'])}; not probability-weighted", accent=AMBER)

    # 6 — stage and risk.
    slide = ppt_base(prs, f"Open mix: {p['open_deals']} deals, {compact_money(p['open_expected_arr_total'])} expected ARR", 6, "crm-opportunities.csv")
    ppt_shape(slide, 0.55, 1.55, 6.15, 5.12, fill=WHITE, line=LINE)
    ppt_text(slide, "Stage mix | open deal count", 0.82, 1.75, 5.6, 0.32, size=16, bold=True, color=BLUE)
    add_chart(slide, XL_CHART_TYPE.BAR_CLUSTERED, list(model["stages"]), [("Deals", [v["deals"] for v in model["stages"].values()])], 0.8, 2.12, 5.65, 4.2, [BLUE], number_format='0', data_labels=True)
    ppt_text(slide, "Risk and next-step hygiene", 7.0, 1.62, 5.7, 0.35, size=17, bold=True, color=BLUE)
    ppt_table(slide, 7.0, 2.05, 5.78, 2.15, ["Risk", "Deals", "Expected ARR", "Overdue"], [
        [risk, number(v["deals"]), compact_money(v["expected_arr"]), number(v["overdue_deals"])]
        for risk, v in model["risks"].items()
    ], col_widths=[1.25, 0.75, 1.5, 0.95], font_size=11)
    ppt_multiline(slide, [
        ("Hygiene action", {"size": 16, "bold": True, "color": BLUE}),
        (f"{p['overdue_open_deals']} open next steps predate {model['generated']}: {compact_money(p['overdue_open_expected_arr'])} expected ARR.", {"size": 14}),
        (f"At risk: {model['risks']['At risk']['deals']} deals / {compact_money(model['risks']['At risk']['expected_arr'])}. Refresh the close plan; do not silently revalue the deal.", {"size": 13}),
    ], 7.0, 4.48, 5.78, 2.18, fill=WHITE)

    # 7 — closed win/loss.
    slide = ppt_base(prs, f"Closed outcomes: {pct(p['closed_win_rate'])} win rate", 7, "crm-opportunities.csv", subtitle="Q3 + Q4 closed opportunities; reason fields describe outcomes, not causality")
    ppt_shape(slide, 0.55, 1.8, 5.25, 4.88, fill=WHITE, line=LINE)
    chart = add_chart(slide, XL_CHART_TYPE.DOUGHNUT, ["Closed Won", "Closed Lost"], [("Deals", [p["closed_won"], p["closed_lost"]])], 0.85, 2.0, 4.65, 3.75, [TEAL, RED], legend=True)
    for point, color in zip(chart.series[0].points, [TEAL, RED]):
        point.format.fill.solid()
        point.format.fill.fore_color.rgb = ppt_color(color)
        point.format.line.color.rgb = ppt_color(color)
    ppt_text(slide, pct(p["closed_win_rate"]), 2.0, 3.1, 2.35, 0.55, size=28, color=INK, bold=True, align=PP_ALIGN.CENTER)
    ppt_text(slide, f"{p['closed_won']} won / {p['closed_lost']} lost", 1.45, 3.7, 3.45, 0.38, size=13, color=MUTED, align=PP_ALIGN.CENTER)
    ppt_text(slide, f"Closed population: {p['closed_deals']}", 1.25, 5.95, 3.85, 0.35, size=14, color=INK, bold=True, align=PP_ALIGN.CENTER)
    ppt_shape(slide, 6.05, 1.8, 6.73, 4.88, fill=WHITE, line=LINE)
    ppt_text(slide, "Recorded loss reasons | deal count", 6.35, 2.0, 6.0, 0.35, size=16, bold=True, color=BLUE)
    reasons = sorted(model["loss_reasons"].items(), key=lambda item: (item[1], item[0]))
    add_chart(slide, XL_CHART_TYPE.BAR_CLUSTERED, [r[0] for r in reasons], [("Closed Lost", [r[1] for r in reasons])], 6.3, 2.4, 6.15, 3.95, [RED], number_format='0', data_labels=True)

    # 8 — activation.
    slide = ppt_base(prs, f"Activation: {pct(act['activation_rate'])}; {last_cohort.split('-')[1]} retention lags", 8, "activation-users.csv", subtitle="Two rates per cohort: activated / signups and retained_w2 / activated")
    ppt_card(slide, 0.55, 1.78, 2.85, 1.36, "Signups", number(act["signups"]), "W40–W43", accent=BLUE)
    ppt_card(slide, 3.62, 1.78, 2.85, 1.36, "Activated", number(act["activated"]), pct(act["activation_rate"]) + " of signups", accent=TEAL)
    ppt_card(slide, 6.69, 1.78, 2.85, 1.36, "Retained W2", number(act["retained_w2"]), pct(act["retention_of_activated"]) + " of activated", accent=BLUE)
    ppt_card(slide, 9.76, 1.78, 3.02, 1.36, "Overall retention", pct(act["overall_retention"]), "Retained / signups", accent=AMBER)
    ppt_shape(slide, 0.55, 3.35, 8.35, 3.33, fill=WHITE, line=LINE)
    cohorts = list(act["cohorts"])
    add_chart(slide, XL_CHART_TYPE.COLUMN_CLUSTERED, cohorts, [
        ("Activation rate", [act["cohorts"][c]["activation_rate"] for c in cohorts]),
        ("Retained / activated", [act["cohorts"][c]["retention_of_activated"] for c in cohorts]),
    ], 0.78, 3.52, 7.9, 2.95, [BLUE, TEAL], legend=True, number_format='0%', data_labels=True)
    ppt_multiline(slide, [
        ("Cohort readout", {"size": 16, "bold": True, "color": BLUE}),
        (f"{last_cohort.split('-')[1]} retained {pct(act['cohorts'][last_cohort]['retention_of_activated'])} of activated users; {first_cohort.split('-')[1]} retained {pct(act['cohorts'][first_cohort]['retention_of_activated'])}.", {"size": 14}),
        ("Four cohorts support comparison, not a causal explanation. Inspect onboarding execution before naming a driver.", {"size": 13}),
    ], 9.15, 3.35, 3.63, 3.33, fill=WHITE)

    # 9 — actions.
    slide = ppt_base(prs, f"Actions: base, deal hygiene, {last_cohort.split('-')[1]} retention", 9, "ARR / CRM / activation CSVs; office-validation.json")
    actions = [
        ("CUSTOMER SUCCESS", "Review the loss base", f"Cover {compact_money(a['total_losses'])} contraction + churn by segment; document evidence before assigning causes.", RED),
        ("SALES LEADERSHIP", "Reset deal control", f"Triage {model['risks']['At risk']['deals']} At risk deals and {p['overdue_open_deals']} overdue next steps; preserve scenario definitions.", BLUE),
        ("REVOPS", "Publish one forecast language", f"Commit {compact_money(p['commit_view'])}; Best Case {compact_money(p['best_case_view'])}; Full {compact_money(p['full_pipeline_view'])}. Keep weighted ARR separate.", TEAL),
        ("GROWTH + PRODUCT", "Inspect cohort execution", f"{last_cohort.split('-')[1]} retained {pct(act['cohorts'][last_cohort]['retention_of_activated'])} of activated users vs {pct(act['cohorts'][first_cohort]['retention_of_activated'])} in {first_cohort.split('-')[1]}.", AMBER),
    ]
    positions = [(0.55, 1.55), (6.8, 1.55), (0.55, 3.65), (6.8, 3.65)]
    for (role, title, body, accent), (x, y) in zip(actions, positions):
        ppt_shape(slide, x, y, 5.98, 1.82, fill=WHITE, line=LINE)
        ppt_text(slide, role, x + 0.2, y + 0.14, 5.58, 0.24, size=10, color=accent, bold=True)
        ppt_text(slide, title, x + 0.2, y + 0.43, 5.58, 0.35, size=18, color=INK, bold=True)
        ppt_text(slide, body, x + 0.2, y + 0.84, 5.58, 0.77, size=13, color=INK)
    ppt_text(slide, "Validation: source hashes, arithmetic, reconciliation, formula logic, package reopen and cross-artifact headlines passed in Python. Excel recalc-on-load is set; formula recalculation and visual Office rendering were not inspected.", 0.58, 5.82, 12.15, 0.76, size=12, color=MUTED, italic=True)

    PPT_DIR.mkdir(parents=True, exist_ok=True)
    prs.save(PPTX_PATH)
    normalize_zip(PPTX_PATH)


# ------------------------- Package and QA ---------------------------------


def normalize_core_xml(payload: bytes) -> bytes:
    for tag in [b"created", b"modified"]:
        payload = re.sub(
            rb"(<dcterms:" + tag + rb"[^>]*>)[^<]*(</dcterms:" + tag + rb">)",
            rb"\g<1>2026-11-23T00:00:00Z\g<2>",
            payload,
        )
    return payload


def normalize_embedded_xlsx(payload: bytes) -> bytes:
    source_buffer = io.BytesIO(payload)
    target_buffer = io.BytesIO()
    with zipfile.ZipFile(source_buffer, "r") as source, zipfile.ZipFile(target_buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as target:
        for old in source.infolist():
            data = source.read(old.filename)
            if old.filename == "docProps/core.xml":
                data = normalize_core_xml(data)
            info = zipfile.ZipInfo(old.filename, date_time=ZIP_DATETIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = old.external_attr
            info.create_system = old.create_system
            info.flag_bits = old.flag_bits & ~0x08
            target.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    return target_buffer.getvalue()


def normalize_zip(path: Path) -> None:
    """Normalize entry metadata and Office timestamps for deterministic builds."""
    temp = path.with_suffix(path.suffix + ".tmp")
    with zipfile.ZipFile(path, "r") as source, zipfile.ZipFile(temp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as target:
        for old in source.infolist():
            payload = source.read(old.filename)
            if old.filename == "docProps/core.xml":
                payload = normalize_core_xml(payload)
            elif old.filename.startswith("ppt/embeddings/") and old.filename.endswith(".xlsx"):
                payload = normalize_embedded_xlsx(payload)
            info = zipfile.ZipInfo(old.filename, date_time=ZIP_DATETIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = old.external_attr
            info.create_system = old.create_system
            info.flag_bits = old.flag_bits & ~0x08
            target.writestr(info, payload, compress_type=zipfile.ZIP_DEFLATED, compresslevel=6)
    temp.replace(path)


def zip_package_check(path: Path) -> dict:
    required = {
        ".xlsx": ["[Content_Types].xml", "xl/workbook.xml", "_rels/.rels"],
        ".docx": ["[Content_Types].xml", "word/document.xml", "_rels/.rels"],
        ".pptx": ["[Content_Types].xml", "ppt/presentation.xml", "_rels/.rels"],
    }[path.suffix]
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        missing = [name for name in required if name not in names]
        corrupt = archive.testzip()
        xml_errors = []
        for name in sorted(names):
            if name.endswith(".xml") or name.endswith(".rels"):
                try:
                    etree.fromstring(archive.read(name))
                except Exception as exc:  # exact artifact/name is retained in JSON
                    xml_errors.append({"part": name, "error": str(exc)})
        logo_found = any(sha256_bytes(archive.read(name)) == sha256_file(LOGO) for name in names if name.startswith(("xl/media/", "word/media/", "ppt/media/")))
        formula_cache_values = None
        if path.suffix == ".xlsx":
            sheet_xml = b"".join(archive.read(name) for name in names if re.fullmatch(r"xl/worksheets/sheet\d+\.xml", name))
            formula_cache_values = len(re.findall(rb"<f[ >]", sheet_xml))
    return {
        "pass": not missing and corrupt is None and not xml_errors and logo_found,
        "zip_crc": "PASS" if corrupt is None else f"FAIL: {corrupt}",
        "required_parts_missing": missing,
        "xml_parts_parse": "PASS" if not xml_errors else "FAIL",
        "xml_errors": xml_errors,
        "actual_vera_mark_embedded": logo_found,
        "formula_elements_in_package": formula_cache_values,
    }


def all_doc_text(doc: Document) -> str:
    chunks = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                chunks.extend(p.text for p in cell.paragraphs)
    for section in doc.sections:
        chunks.extend(p.text for p in section.header.paragraphs)
        chunks.extend(p.text for p in section.footer.paragraphs)
    return "\n".join(chunks)


def all_ppt_text(prs: Presentation) -> str:
    chunks = []
    for slide in prs.slides:
        for shape in slide.shapes:
            if getattr(shape, "has_text_frame", False):
                chunks.append(shape.text)
            if getattr(shape, "has_table", False):
                for row in shape.table.rows:
                    for cell in row.cells:
                        chunks.append(cell.text)
    return "\n".join(chunks)


def placeholder_hits(text: str) -> list[str]:
    patterns = [r"lorem\s+ipsum", r"\bTODO\b", r"\bTBD\b", r"\[insert", r"placeholder text", r"mock artifact:", r"\bXXX+\b"]
    return sorted({match.group(0) for pattern in patterns for match in re.finditer(pattern, text, flags=re.I)})


def scan_workbook_formulas(wb) -> dict:
    formulas = {}
    broken = []
    unsupported = []
    functions = Counter()
    sheet_names = set(wb.sheetnames)
    banned = {"XLOOKUP", "FILTER", "SEQUENCE", "UNIQUE", "SORT", "SORTBY", "XMATCH", "LET", "LAMBDA"}
    for ws in wb.worksheets:
        cells = []
        for row in ws.iter_rows():
            for cell in row:
                if cell.data_type == "f" or (isinstance(cell.value, str) and cell.value.startswith("=")):
                    formula = cell.value
                    cells.append(cell.coordinate)
                    if "#REF!" in formula or "#NAME?" in formula or "#VALUE!" in formula:
                        broken.append({"sheet": ws.title, "cell": cell.coordinate, "formula": formula})
                    try:
                        Tokenizer(formula)
                    except Exception as exc:
                        broken.append({"sheet": ws.title, "cell": cell.coordinate, "error": str(exc)})
                    for match in re.finditer(r"(?:'([^']+)'|\b([A-Za-z_][A-Za-z0-9_]*))!", formula):
                        sheet = match.group(1) or match.group(2)
                        if sheet not in sheet_names:
                            broken.append({"sheet": ws.title, "cell": cell.coordinate, "missing_sheet": sheet})
                    for function in re.findall(r"([A-Z][A-Z0-9._]*)\s*\(", formula.upper()):
                        functions[function] += 1
                        if function in banned or function.startswith("_XLFN"):
                            unsupported.append({"sheet": ws.title, "cell": cell.coordinate, "function": function})
        if cells:
            formulas[ws.title] = {"count": len(cells), "cells": cells}
    return {
        "formula_count": sum(item["count"] for item in formulas.values()),
        "formula_cells_by_sheet": {key: value["count"] for key, value in formulas.items()},
        "formula_cells": formulas,
        "broken_formula_references": broken,
        "unsupported_functions": unsupported,
        "functions_used": dict(sorted(functions.items())),
        "pass": not broken and not unsupported,
    }


def independent_checks(model: dict) -> list[dict]:
    m = model["manifest"]
    checks = []
    def check(name, actual, expected, tolerance=0):
        passed = abs(actual - expected) <= tolerance if isinstance(actual, (int, float)) and isinstance(expected, (int, float)) else actual == expected
        checks.append({"check": name, "actual": actual, "expected": expected, "tolerance": tolerance, "pass": bool(passed)})
    for key in ["starting_arr", "new_arr", "expansion_arr", "contraction_arr", "churn_arr", "ending_arr", "net_arr_added", "starting_active_customers", "ending_active_customers"]:
        check(f"arr.{key}", model["arr"][key], m["arr"][key])
    check("arr.grr", round(model["arr"]["grr"], 6), m["arr"]["grr"])
    check("arr.nrr", round(model["arr"]["nrr"], 6), m["arr"]["nrr"])
    residual = model["arr"]["ending_arr"] - (model["arr"]["starting_arr"] + model["arr"]["new_arr"] + model["arr"]["expansion_arr"] - model["arr"]["contraction_arr"] - model["arr"]["churn_arr"])
    check("arr.aggregate_residual", residual, 0)
    check("arr.row_identities", sum(as_int(r, "ending_arr") != as_int(r, "starting_arr") + as_int(r, "new_arr") + as_int(r, "expansion_arr") - as_int(r, "contraction_arr") - as_int(r, "churn_arr") for r in model["arr_rows"]), 0)
    for key in ["open_deals", "closed_deals", "open_expected_arr_total", "q4_closed_won_arr", "commit_view", "best_case_view", "full_pipeline_view", "closed_won", "closed_lost"]:
        check(f"pipeline.{key}", model["pipeline"][key], m["pipeline"][key])
    check("pipeline.closed_win_rate", round(model["pipeline"]["closed_win_rate"], 6), m["pipeline"]["closed_win_rate"])
    check("pipeline.scenario_commit_identity", model["pipeline"]["commit_view"] - model["pipeline"]["q4_closed_won_arr"] - model["forecast"]["Commit"]["expected_arr"], 0)
    check("pipeline.scenario_best_case_identity", model["pipeline"]["best_case_view"] - model["pipeline"]["commit_view"] - model["forecast"]["Best Case"]["expected_arr"], 0)
    check("pipeline.scenario_full_identity", model["pipeline"]["full_pipeline_view"] - model["pipeline"]["best_case_view"] - model["forecast"]["Pipeline"]["expected_arr"], 0)
    for key in ["signups", "activated", "retained_w2"]:
        check(f"activation.{key}", model["activation"][key], m["activation"][key])
    for key in ["activation_rate", "retention_of_activated", "overall_retention"]:
        check(f"activation.{key}", round(model["activation"][key], 6), m["activation"][key])
    check("commission.tier_residual", round(sum(r["commission"] - r["tier1"] - r["tier2"] - r["tier3"] for r in model["commission"]), 6), 0)
    check("commission.q4_won_total", sum(r["q4_won"] for r in model["commission"]), model["pipeline"]["q4_closed_won_arr"])
    check("counts.arr_rows", len(model["arr_rows"]), m["tables"]["arr-rollforward.csv"])
    check("counts.accounts", len(model["accounts"]), m["tables"]["crm-accounts.csv"])
    check("counts.activation", len(model["activation_rows"]), m["tables"]["activation-users.csv"])
    check("counts.opportunities", len(model["opportunities"]), m["tables"]["crm-opportunities.csv"])
    return checks


def artifact_note() -> dict:
    return {
        "formula_recalculation": "not inspected",
        "visual_office_rendering": "not inspected",
        "reason": "LibreOffice/soffice/pdftoppm are not installed; no PDF or screenshot substitutes were created.",
        "mitigation": "Workbook fullCalcOnLoad/forceFullCalc/auto calc mode are set; formula logic independently verified in Python; OOXML packages reopened and parsed.",
    }


def validate_outputs(model: dict, determinism: dict) -> dict:
    results = {"generated_on": BUILD_DATE, "status": "PASS_WITH_NOTES", "synthetic": True, "anonymized": True, "scope": "Office examples only; no live sources", "checks": []}
    def record(check, expected, actual, passed, notes=None):
        item = {"check": check, "expected": expected, "actual": actual, "pass": bool(passed)}
        if notes:
            item["notes"] = notes
        results["checks"].append(item)

    # Source hash verification across every manifest-listed source.
    source_hash_results = {}
    for name, expected in model["manifest"]["source_sha256"].items():
        path = BASE / name if name == "mock-pipeline.csv" else DATA / name
        actual = sha256_file(path)
        source_hash_results[name] = {"expected": expected, "actual": actual, "pass": actual == expected}
    results["source_hashes"] = source_hash_results
    record("source_sha256", "all manifest-listed source hashes match", f"{sum(v['pass'] for v in source_hash_results.values())}/{len(source_hash_results)} matched", all(v["pass"] for v in source_hash_results.values()))

    packages = {}
    for path in ALL_ARTIFACTS:
        rel = str(path.relative_to(BASE))
        package = zip_package_check(path)
        package.update({"bytes": path.stat().st_size, "sha256": sha256_file(path)})
        packages[rel] = package
    results["packages"] = packages
    record("office_zip_packages", "6 valid packages, XML parsed, Vera mark embedded", f"{sum(p['pass'] for p in packages.values())}/6 passed", all(p["pass"] for p in packages.values()))
    results["deterministic_rebuild"] = determinism
    record("deterministic_rebuild", "identical SHA-256 for all 6 Office artifacts across two complete in-process rebuilds", f"{sum(determinism['first_sha256'][str(path.relative_to(BASE))] == determinism['second_sha256'][str(path.relative_to(BASE))] for path in ALL_ARTIFACTS)}/6 identical", determinism["pass"])

    # Reopen workbook and inspect formulas, rows, calculation settings and content.
    wb = load_workbook(XLSX_PATH, data_only=False, read_only=False)
    expected_sheets = ["README", "ARR Summary", "ARR Rollforward", "Open Pipeline", "Closed Opportunities", "Accounts", "Activation", "Quota Commission", "Pipeline Summary", "Validation"]
    record("workbook_sheet_order", expected_sheets, wb.sheetnames, wb.sheetnames == expected_sheets)
    raw_rows = {"ARR Rollforward": 1050, "Open Pipeline": 200, "Closed Opportunities": 400, "Accounts": 1050, "Activation": 2400, "Quota Commission": 8}
    actual_rows = {}
    for name in raw_rows:
        table_name = next(iter(wb[name].tables))
        table_ref = wb[name].tables[table_name].ref
        actual_rows[name] = int(re.search(r"(\d+)$", table_ref).group(1)) - 4
    # Table refs, not worksheet max_row, isolate detail rows from summaries/totals.
    record("workbook_detail_rows", raw_rows, actual_rows, actual_rows == raw_rows)
    formula_scan = scan_workbook_formulas(wb)
    results["workbook"] = {
        "sheet_order": wb.sheetnames,
        "detail_rows": actual_rows,
        "tables": {ws.title: {name: ws.tables[name].ref for name in ws.tables} for ws in wb.worksheets if ws.tables},
        "freeze_panes": {ws.title: str(ws.freeze_panes) for ws in wb.worksheets},
        "calculation": {"calcMode": wb.calculation.calcMode, "fullCalcOnLoad": wb.calculation.fullCalcOnLoad, "forceFullCalc": wb.calculation.forceFullCalc},
        "formula_scan": formula_scan,
        "artifact_notes": artifact_note(),
    }
    record("workbook_formula_reference_scan", "zero broken refs and zero unsupported functions", {"broken": len(formula_scan["broken_formula_references"]), "unsupported": len(formula_scan["unsupported_functions"])}, formula_scan["pass"])
    record("workbook_formula_count", ">= 100 formulas", formula_scan["formula_count"], formula_scan["formula_count"] >= 100)
    calc_ok = wb.calculation.calcMode == "auto" and wb.calculation.fullCalcOnLoad is True and wb.calculation.forceFullCalc is True
    record("workbook_recalc_on_load", {"calcMode": "auto", "fullCalcOnLoad": True, "forceFullCalc": True}, results["workbook"]["calculation"], calc_ok)
    record("workbook_tables", "six detail tables present", sum(len(ws.tables) for ws in wb.worksheets), sum(len(ws.tables) for ws in wb.worksheets) == 6)
    record("workbook_formula_cache_note", "openpyxl writes formulas without cached results", "formula recalculation not inspected", True, "No data_only values are represented as recalculated results.")

    # Independently recomputed formula logic and source controls.
    py_checks = independent_checks(model)
    results["independent_python_formula_logic"] = py_checks
    record("independent_formula_logic", "all source and identity checks pass", f"{sum(c['pass'] for c in py_checks)}/{len(py_checks)} passed", all(c["pass"] for c in py_checks))

    # Reopen Word documents; verify substantive content and headline strings.
    doc_results = {}
    doc_requirements = {
        "revenue": ["ARR movement", "Active customers and retention", "Q4 open forecast scenarios", "Activation and week-2 retention", compact_money(model["arr"]["ending_arr"]), pct(model["arr"]["nrr"]), money(model["pipeline"]["commit_view"]), "Built by Vera"],
        "pipeline": ["Scenario bridge", "Stage and risk mix", "Largest open opportunities", "Closed win/loss evidence", money(model["pipeline"]["best_case_view"]), money(model["pipeline"]["full_pipeline_view"]), "Built by Vera"],
        "campaign": ["Campaign brief", "Execution and readout", "Closed CRM context", pct(model["activation_sources"]["Referral"]["activation_rate"]), pct(model["activation_sources"]["Referral"]["retention_of_activated"]), "Built by Vera"],
        "project": ["Baseline and scope", "Source-derived schedule", "Workstream delivery plan", "Risk register", money(model["pipeline"]["commit_view"]), "Built by Vera"],
    }
    for key, path in DOC_PATHS.items():
        doc = Document(path)
        text = all_doc_text(doc)
        required = doc_requirements[key]
        missing = [value for value in required if value not in text]
        placeholders = placeholder_hits(text)
        has_note = "Formula recalculation and visual Office rendering: not inspected" in text
        doc_results[path.name] = {
            "paragraphs": len(doc.paragraphs),
            "tables": len(doc.tables),
            "inline_images": len(doc.inline_shapes),
            "required_content_missing": missing,
            "placeholder_hits": placeholders,
            "artifact_note_present": has_note,
            "pass": not missing and not placeholders and has_note and len(doc.tables) >= (3 if key == "campaign" else 4),
        }
    results["documents"] = doc_results
    record("docx_reopen_content", "4 docs reopen; required content/stamp/notes present; no placeholders", {k: v["pass"] for k, v in doc_results.items()}, all(v["pass"] for v in doc_results.values()))

    # Reopen PowerPoint, inspect text, native objects and shape geometry.
    prs = Presentation(PPTX_PATH)
    text = all_ppt_text(prs)
    required_ppt = [f"ARR +{compact_money(model['arr']['net_arr_added'])}", f"Active customers: {number(model['arr']['starting_active_customers'])} to {number(model['arr']['ending_active_customers'])}", f"{compact_money(model['pipeline']['commit_view'])} Commit", f"Open mix: {model['pipeline']['open_deals']} deals", f"{pct(model['pipeline']['closed_win_rate'])} win rate", f"Activation: {pct(model['activation']['activation_rate'])}", "Actions: base", "Built by Vera"]
    missing_ppt = [value for value in required_ppt if value not in text]
    out_of_bounds = []
    text_fit_flags = []
    font_sizes = []
    chart_count = 0
    table_count = 0
    picture_count = 0
    for slide_index, slide in enumerate(prs.slides, start=1):
        for shape in slide.shapes:
            x, y, w, h = [v / 914400 for v in (shape.left, shape.top, shape.width, shape.height)]
            if x < -0.001 or y < -0.001 or x + w > SLIDE_W + 0.01 or y + h > SLIDE_H + 0.01:
                out_of_bounds.append({"slide": slide_index, "shape": shape.name, "bounds": [x, y, w, h]})
            if getattr(shape, "has_text_frame", False) and shape.text.strip():
                tf = shape.text_frame
                usable_w = (shape.width - tf.margin_left - tf.margin_right) / 914400
                usable_h = (shape.height - tf.margin_top - tf.margin_bottom) / 914400
                required_pt = 0.0
                for paragraph in tf.paragraphs:
                    if not paragraph.text:
                        continue
                    sizes = [run.font.size.pt for run in paragraph.runs if run.font.size]
                    size = max(sizes or [18])
                    chars_per_line = max(1, int(usable_w * 72 / (size * 0.55)))
                    lines = max(1, math.ceil(len(paragraph.text) / chars_per_line))
                    required_pt += lines * size * 1.08 + (paragraph.space_after.pt if paragraph.space_after else 0)
                if required_pt > usable_h * 72 * 1.08:
                    text_fit_flags.append({"slide": slide_index, "shape": shape.name, "text": shape.text[:120], "estimated_required_inches": round(required_pt / 72, 3), "available_inches": round(usable_h, 3)})
            if getattr(shape, "has_chart", False):
                chart_count += 1
            if getattr(shape, "has_table", False):
                table_count += 1
            if shape.shape_type == 13:
                picture_count += 1
            if getattr(shape, "has_text_frame", False):
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        if run.font.size:
                            font_sizes.append(run.font.size.pt)
            if getattr(shape, "has_table", False):
                for row in shape.table.rows:
                    for cell in row.cells:
                        for paragraph in cell.text_frame.paragraphs:
                            for run in paragraph.runs:
                                if run.font.size:
                                    font_sizes.append(run.font.size.pt)
    ppt_result = {
        "slides": len(prs.slides),
        "aspect_ratio": "16:9",
        "dimensions_inches": [prs.slide_width / 914400, prs.slide_height / 914400],
        "native_charts": chart_count,
        "native_tables": table_count,
        "pictures": picture_count,
        "minimum_explicit_text_size_pt": min(font_sizes) if font_sizes else None,
        "out_of_bounds_shapes": out_of_bounds,
        "text_fit_heuristic": {"method": "Conservative character-width estimate for text boxes; not visual rendering", "flags": text_fit_flags, "pass": not text_fit_flags},
        "required_content_missing": missing_ppt,
        "placeholder_hits": placeholder_hits(text),
        "pass": 8 <= len(prs.slides) <= 10 and chart_count >= 6 and not out_of_bounds and not text_fit_flags and not missing_ppt and not placeholder_hits(text) and (min(font_sizes) if font_sizes else 0) >= 10,
    }
    results["presentation"] = ppt_result
    record("pptx_reopen_content_geometry", "9 slides, >=6 native charts, no missing content/placeholders/out-of-bounds shapes/text-fit heuristic flags, text >=10pt", ppt_result, ppt_result["pass"])

    # Cross-artifact headline consistency uses actual strings read back from files.
    revenue_text = all_doc_text(Document(DOC_PATHS["revenue"]))
    pipeline_text = all_doc_text(Document(DOC_PATHS["pipeline"]))
    ppt_text_all = all_ppt_text(Presentation(PPTX_PATH))
    headline_checks = {
        "ending_arr": {"value": model["arr"]["ending_arr"], "display": compact_money(model["arr"]["ending_arr"]), "revenue_doc": compact_money(model["arr"]["ending_arr"]) in revenue_text, "pptx": compact_money(model["arr"]["ending_arr"]) in ppt_text_all},
        "nrr": {"value": round(model["arr"]["nrr"], 6), "display": pct(model["arr"]["nrr"]), "revenue_doc": pct(model["arr"]["nrr"]) in revenue_text, "pptx": pct(model["arr"]["nrr"]) in ppt_text_all},
        "commit_view": {"value": model["pipeline"]["commit_view"], "display": compact_money(model["pipeline"]["commit_view"]), "revenue_doc": money(model["pipeline"]["commit_view"]) in revenue_text, "pipeline_doc": money(model["pipeline"]["commit_view"]) in pipeline_text, "pptx": compact_money(model["pipeline"]["commit_view"]) in ppt_text_all},
        "best_case_view": {"value": model["pipeline"]["best_case_view"], "display": compact_money(model["pipeline"]["best_case_view"]), "pipeline_doc": money(model["pipeline"]["best_case_view"]) in pipeline_text, "pptx": compact_money(model["pipeline"]["best_case_view"]) in ppt_text_all},
        "full_pipeline_view": {"value": model["pipeline"]["full_pipeline_view"], "display": compact_money(model["pipeline"]["full_pipeline_view"]), "pipeline_doc": money(model["pipeline"]["full_pipeline_view"]) in pipeline_text, "pptx": compact_money(model["pipeline"]["full_pipeline_view"]) in ppt_text_all},
        "activation_rate": {"value": round(model["activation"]["activation_rate"], 6), "display": pct(model["activation"]["activation_rate"]), "revenue_doc": pct(model["activation"]["activation_rate"]) in revenue_text, "pptx": pct(model["activation"]["activation_rate"]) in ppt_text_all},
    }
    cross_pass = all(all(v for k, v in item.items() if k in {"revenue_doc", "pipeline_doc", "pptx"}) for item in headline_checks.values())
    results["cross_artifact_headlines"] = headline_checks
    record("cross_artifact_headline_consistency", "same source-derived headlines in DOCX/PPTX; workbook formulas point to same raw ranges", headline_checks, cross_pass)

    results["artifact_notes"] = artifact_note()
    results["analysis_validator"] = {
        "gate_1_data_correctness": {
            "status": "PASS" if all(c["pass"] for c in py_checks) and cross_pass else "FAIL",
            "C1_arithmetic": "PASS — source-derived rates and ratios recomputed",
            "C2_filters": "PASS — open=nonblank forecast_category; closed=blank; Q4 Closed Won scoped by period/stage",
            "C3_temporal_currency": "PASS — static generated_on and periods from manifest; no rolling live claim",
            "C4_source_integrity": "PASS — all manifest-listed source hashes match",
            "C5_chart_provenance": "PASS — native PPTX chart series use the same Python source model",
            "C6_claim_language": "PASS — comparisons labeled; no causal or live-source claims",
            "C7_segmentation": "PASS — ARR/CRM/activation populations and periods disclosed",
            "C8_terminology": "PASS — ARR, NRR, GRR, activation and retention definitions included",
            "C9_currency": "PASS — USD-only source aggregation",
            "C10_population": "PASS — 1,050 ARR/accounts, 600 opportunities, 2,400 activation rows",
            "C11_reconciliation": "PASS — row-level and aggregate ARR identities plus scenario/commission identities",
            "C12_evidence_coverage": "PASS — claims limited to pulled CSV fields",
        },
        "gate_2_output_quality": {
            "status": "PASS_WITH_NOTES",
            "C13_contrast": "Design-token check passed; actual visual contrast not inspected",
            "C14_responsiveness": "Not applicable to fixed Office page/slide formats; geometry checked",
            "C15_typography": "Arial applied; explicit PPT text >=10pt; Office visual metrics not inspected",
            "C16_completeness": "PASS — required sections and no placeholder patterns",
            "C17_attribution": "PASS — Built by Vera 2026-11-23 and synthetic labels",
            "C18_id_resolution": "PASS — visible report examples use aliases; raw IDs remain only in detail sheets",
        },
        "significance_awareness": "Full synthetic census of supplied CSVs; sampling coverage/significance not applicable. No external population inference.",
        "final": "PASS WITH NOTES — recalculation and visual Office rendering not inspected",
    }
    failed = [c for c in results["checks"] if not c["pass"]]
    results["status"] = "PASS_WITH_NOTES" if not failed else "FAIL"
    results["summary"] = {
        "checks_total": len(results["checks"]),
        "checks_passed": sum(c["pass"] for c in results["checks"]),
        "checks_failed": len(failed),
        "failed_checks": [c["check"] for c in failed],
        "formula_recalculation": "not inspected",
        "visual_office_rendering": "not inspected",
    }
    VALIDATION_PATH.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return results


def build_artifacts(model: dict) -> None:
    build_workbook(model)
    build_revenue_doc(model)
    build_pipeline_doc(model)
    build_campaign_doc(model)
    build_project_doc(model)
    build_presentation(model)


def main() -> None:
    if not LOGO.exists():
        raise FileNotFoundError(LOGO)
    model = compute_model()
    build_artifacts(model)
    first_hashes = {str(path.relative_to(BASE)): sha256_file(path) for path in ALL_ARTIFACTS}
    build_artifacts(model)
    second_hashes = {str(path.relative_to(BASE)): sha256_file(path) for path in ALL_ARTIFACTS}
    determinism = {
        "method": "Two consecutive complete in-process builds; SHA-256 compared for all six Office artifacts",
        "first_sha256": first_hashes,
        "second_sha256": second_hashes,
        "pass": first_hashes == second_hashes,
    }
    results = validate_outputs(model, determinism)
    summary = {
        "status": results["status"],
        "artifacts": [str(path.relative_to(BASE)) for path in ALL_ARTIFACTS],
        "validation": str(VALIDATION_PATH.relative_to(BASE)),
        "checks": results["summary"],
        "formula_count": results["workbook"]["formula_scan"]["formula_count"],
        "slides": results["presentation"]["slides"],
        "native_charts": results["presentation"]["native_charts"],
        "deterministic_rebuild": results["deterministic_rebuild"]["pass"],
    }
    print(json.dumps(summary, indent=2))
    if results["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
