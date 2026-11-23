#!/usr/bin/env python3
"""Build every Vera HTML example deterministically from the approved CSV snapshot."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

sys.dont_write_bytecode = True

from html_common import (
    Raw,
    TOKENS,
    badge,
    bar_list,
    compact_money,
    esc,
    fmt_int,
    kpis,
    link,
    logo_data,
    money,
    page,
    pct,
    section,
    signed_money,
    so_what,
    table,
    write_json_script,
)

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
STAGING = BASE.parents[3]
MANIFEST_PATH = DATA / "manifest.json"
BUILD_DATE = "2026-11-23"
STAGE_ORDER = ["Discovery", "Validation", "Proposal", "Negotiation"]
FORECAST_ORDER = ["Commit", "Best Case", "Pipeline"]
RISK_ORDER = ["On track", "Watch", "At risk"]
FUTURE_LINKS = {
    "data/data-dictionary.md",
    "documents/mock-revenue-review.docx",
    "documents/mock-pipeline-review.docx",
    "documents/mock-campaign-one-pager.docx",
    "documents/mock-project-plan.docx",
    "presentations/mock-revenue-review.pptx",
}
REQUIRED_OUTPUTS = [
    "mock-arr-waterfall.html",
    "mock-briefing-email.html",
    "mock-forecast.html",
    "mock-slides.html",
    "mock-activation-funnel.html",
    "mock-weekly-recap.html",
    "tour/mock-revenue-dashboard.html",
    "tour/pipeline-motion.html",
    "tour/campaign-one-pager.html",
    "tour/win-loss-brief.html",
    "tour/pipeline-analysis.html",
    "tour/quota-commission.html",
    "tour/project-plan.html",
    "index.html",
]


def read_rows(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def integer(row: dict[str, str], key: str) -> int:
    return int(row[key])


def sum_field(rows: list[dict[str, str]], key: str) -> int:
    return sum(integer(row, key) for row in rows)


def date_label(value: str) -> str:
    return date.fromisoformat(value).strftime("%b %d, %Y").replace(" 0", " ")


def short_period(period: str) -> str:
    return period.replace("2026-", "") + " 2026"


def risk_badge(value: str) -> Raw:
    tone = {"On track": "good", "Watch": "warn", "At risk": "risk"}.get(value, "")
    return badge(value, tone)


def forecast_badge(value: str) -> Raw:
    tone = {"Commit": "good", "Best Case": "secondary", "Pipeline": "warn"}.get(value, "")
    return badge(value, tone)


@dataclass
class Context:
    manifest: dict
    rows: dict[str, list[dict[str, str]]]
    logo: str

    @property
    def generated_on(self) -> str:
        return self.manifest["generated_on"]

    @property
    def arr_period(self) -> str:
        return self.manifest["periods"]["arr_rollforward"]

    @property
    def forecast_period(self) -> str:
        return self.manifest["periods"]["pipeline_forecast"]

    @property
    def accounts(self) -> dict[str, dict[str, str]]:
        return {row["account_id"]: row for row in self.rows["crm-accounts.csv"]}

    @property
    def open_opps(self) -> list[dict[str, str]]:
        return [row for row in self.rows["crm-opportunities.csv"] if row["forecast_category"]]

    @property
    def closed_opps(self) -> list[dict[str, str]]:
        return [row for row in self.rows["crm-opportunities.csv"] if not row["forecast_category"]]

    @property
    def owner_names(self) -> dict[str, str]:
        return {row["owner_id"]: row["owner_alias"] for row in self.rows["quota-targets.csv"]}


def source(ctx: Context, name: str, depth: int = 0) -> tuple[str, str, str]:
    prefix = "../" * depth
    if name == "manifest.json":
        href = prefix + "data/manifest.json"
        digest = hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest()
    elif name == "mock-pipeline.csv":
        href = prefix + name
        digest = ctx.manifest["source_sha256"][name]
    else:
        href = prefix + "data/" + name
        digest = ctx.manifest["source_sha256"][name]
    return name, href, digest


def sources(ctx: Context, names: list[str], depth: int = 0) -> list[tuple[str, str, str]]:
    return [source(ctx, name, depth) for name in names]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_context() -> Context:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    names = sorted(manifest["tables"])
    rows = {name: read_rows(name) for name in names}
    with (BASE / "mock-pipeline.csv").open(newline="", encoding="utf-8") as handle:
        mock_pipeline = list(csv.DictReader(handle))
    rows["mock-pipeline.csv"] = mock_pipeline
    ctx = Context(manifest=manifest, rows=rows, logo=logo_data(STAGING))
    validate_sources(ctx)
    return ctx


def validate_sources(ctx: Context) -> None:
    m = ctx.manifest
    require(m["synthetic"] and m["anonymized"], "Dataset must be synthetic and anonymized")
    require(m["generated_on"] == BUILD_DATE, "Unexpected dataset build date")
    for name, expected in m["source_sha256"].items():
        path = BASE / name if name == "mock-pipeline.csv" else DATA / name
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        require(actual == expected, f"Source hash changed: {name}")
    for name, expected in m["tables"].items():
        require(len(ctx.rows[name]) == expected, f"Row count changed: {name}")
    require(all(m["validation"].values()), "Source manifest validation is not clean")

    arr = ctx.rows["arr-rollforward.csv"]
    sums = {key: sum_field(arr, key) for key in ["starting_arr", "new_arr", "expansion_arr", "contraction_arr", "churn_arr", "ending_arr"]}
    require(sums["ending_arr"] == sums["starting_arr"] + sums["new_arr"] + sums["expansion_arr"] - sums["contraction_arr"] - sums["churn_arr"], "ARR does not reconcile")
    for key, value in sums.items():
        require(m["arr"][key] == value, f"ARR manifest mismatch: {key}")
    for row in arr:
        require(row["currency"] == "USD", "Non-USD ARR row")
        require(integer(row, "ending_arr") == integer(row, "starting_arr") + integer(row, "new_arr") + integer(row, "expansion_arr") - integer(row, "contraction_arr") - integer(row, "churn_arr"), "ARR row mismatch")
    require(Counter(row["movement_category"] for row in arr) == Counter(m["arr"]["movement_counts"]), "ARR movement counts differ")
    require(sum(integer(row, "starting_arr") > 0 for row in arr) == m["arr"]["starting_active_customers"], "Starting active customers differ")
    require(sum(integer(row, "ending_arr") > 0 for row in arr) == m["arr"]["ending_active_customers"], "Ending active customers differ")
    start = sums["starting_arr"]
    nrr = (start + sums["expansion_arr"] - sums["contraction_arr"] - sums["churn_arr"]) / start
    grr = (start - sums["contraction_arr"] - sums["churn_arr"]) / start
    require(round(nrr, 6) == m["arr"]["nrr"] and round(grr, 6) == m["arr"]["grr"], "Retention rates differ")

    open_opps, closed = ctx.open_opps, ctx.closed_opps
    p = m["pipeline"]
    require((len(open_opps), len(closed)) == (p["open_deals"], p["closed_deals"]), "Opportunity counts differ")
    require(Counter(row["forecast_category"] for row in open_opps) == Counter(p["open_by_forecast"]), "Forecast category counts differ")
    require(Counter(row["stage"] for row in open_opps) == Counter(p["open_by_stage"]), "Open stage counts differ")
    require(sum(row["stage"] == "Closed Won" for row in closed) == p["closed_won"], "Closed-won count differs")
    require(sum(row["stage"] == "Closed Lost" for row in closed) == p["closed_lost"], "Closed-lost count differs")
    require(len(ctx.rows["mock-pipeline.csv"]) == len(open_opps), "Open extract count differs")
    forecast_sums = {category: sum(integer(r, "expected_arr_usd") for r in open_opps if r["forecast_category"] == category) for category in FORECAST_ORDER}
    require(forecast_sums == {key: p["open_expected_arr_by_forecast"][key] for key in FORECAST_ORDER}, "Forecast sums differ")
    q4_won = sum(integer(r, "expected_arr_usd") for r in closed if r["period"] == ctx.forecast_period and r["stage"] == "Closed Won")
    require(q4_won == p["q4_closed_won_arr"], "Q4 closed-won sum differs")
    require(q4_won + forecast_sums["Commit"] == p["commit_view"], "Commit view differs")
    require(p["commit_view"] + forecast_sums["Best Case"] == p["best_case_view"], "Best case view differs")
    require(p["best_case_view"] + forecast_sums["Pipeline"] == p["full_pipeline_view"], "Full view differs")
    require(sum(forecast_sums.values()) == p["open_expected_arr_total"], "Open ARR sum differs")

    activation = ctx.rows["activation-users.csv"]
    a = m["activation"]
    require(len(activation) == a["signups"], "Signup count differs")
    require(sum(r["activated"] == "true" for r in activation) == a["activated"], "Activation count differs")
    require(sum(r["retained_w2"] == "true" for r in activation) == a["retained_w2"], "Retention count differs")
    require(all(r["activated"] == "true" for r in activation if r["retained_w2"] == "true"), "Retained user was not activated")
    for cohort, expected in a["cohorts"].items():
        subset = [row for row in activation if row["cohort_week"] == cohort]
        actual = {"signups": len(subset), "activated": sum(row["activated"] == "true" for row in subset), "retained_w2": sum(row["retained_w2"] == "true" for row in subset)}
        require(actual == expected, f"Activation cohort differs: {cohort}")


def waterfall_svg(ctx: Context, prefix: str = "arr") -> str:
    a = ctx.manifest["arr"]
    categories = [
        ("Starting ARR", "total", a["starting_arr"], 0, a["starting_arr"]),
        ("New", "gain", a["new_arr"], a["starting_arr"], a["starting_arr"] + a["new_arr"]),
        ("Expansion", "gain", a["expansion_arr"], a["starting_arr"] + a["new_arr"], a["starting_arr"] + a["new_arr"] + a["expansion_arr"]),
        ("Contraction", "loss", -a["contraction_arr"], a["starting_arr"] + a["new_arr"] + a["expansion_arr"] - a["contraction_arr"], a["starting_arr"] + a["new_arr"] + a["expansion_arr"]),
        ("Churn", "loss", -a["churn_arr"], a["ending_arr"], a["starting_arr"] + a["new_arr"] + a["expansion_arr"] - a["contraction_arr"]),
        ("Ending ARR", "total", a["ending_arr"], 0, a["ending_arr"]),
    ]
    width, height = 960, 400
    left, right, top, bottom = 75, 24, 40, 68
    plot_w, plot_h = width - left - right, height - top - bottom
    maximum = max(max(item[3], item[4]) for item in categories)
    baseline = top + plot_h
    step = plot_w / len(categories)
    bar_w = step * 0.56
    colors = {"total": TOKENS["accent"], "gain": TOKENS["good"], "loss": TOKENS["risk"]}

    def y(value: float) -> float:
        return top + plot_h - value / maximum * plot_h

    out = [f'<div class="chart-scroll"><svg viewBox="0 0 {width} {height}" role="img" aria-labelledby="{prefix}-title {prefix}-desc">']
    out.append(f'<title id="{prefix}-title">ARR roll-forward waterfall for {esc(ctx.arr_period)}</title>')
    out.append(f'<desc id="{prefix}-desc">Zero-baseline waterfall. Starting ARR {money(a["starting_arr"])}, new {money(a["new_arr"])}, expansion {money(a["expansion_arr"])}, contraction {money(a["contraction_arr"])}, churn {money(a["churn_arr"])}, ending ARR {money(a["ending_arr"])}. The movement reconciles exactly.</desc>')
    for tick in range(5):
        value = maximum * tick / 4
        yy = y(value)
        out.append(f'<line x1="{left}" y1="{yy:.2f}" x2="{width-right}" y2="{yy:.2f}" stroke="{TOKENS["line"]}" stroke-width="1"/>')
        out.append(f'<text x="{left-10}" y="{yy+4:.2f}" text-anchor="end" font-size="12" fill="{TOKENS["ink"]}">{esc(compact_money(value))}</text>')
    out.append(f'<line x1="{left}" y1="{baseline}" x2="{width-right}" y2="{baseline}" stroke="{TOKENS["ink"]}" stroke-width="2"/>')
    previous_level = None
    for index, (label, kind, value, low, high) in enumerate(categories):
        x = left + step * index + (step - bar_w) / 2
        yy = y(high)
        bar_h = max(2.0, baseline - y(high)) if kind == "total" else max(2.0, abs(y(low) - y(high)))
        if kind == "loss":
            yy = y(high)
        display = money(value) if kind == "total" else signed_money(value)
        compact = compact_money(value) if kind == "total" else ("+" if value >= 0 else "-") + compact_money(abs(value))
        out.append(f'<rect x="{x:.2f}" y="{yy:.2f}" width="{bar_w:.2f}" height="{bar_h:.2f}" rx="5" fill="{colors[kind]}"><title>{esc(label)}: {esc(display)}</title></rect>')
        label_y = max(15, yy - 8)
        out.append(f'<text x="{x+bar_w/2:.2f}" y="{label_y:.2f}" text-anchor="middle" font-size="12" font-weight="700" fill="{TOKENS["ink"]}">{esc(compact)}</text>')
        out.append(f'<text x="{x+bar_w/2:.2f}" y="{baseline+25}" text-anchor="middle" font-size="12" fill="{TOKENS["ink"]}">{esc(label)}</text>')
        current_level = high if kind != "loss" else low
        if previous_level is not None:
            connector_x = left + step * (index - 1) + (step + bar_w) / 2
            out.append(f'<line x1="{connector_x:.2f}" y1="{y(previous_level):.2f}" x2="{x:.2f}" y2="{y(previous_level):.2f}" stroke="{TOKENS["muted"]}" stroke-dasharray="4 4"/>')
        previous_level = current_level
    out.append(f'<text x="{left}" y="{height-10}" font-size="12" fill="{TOKENS["muted"]}">USD, zero baseline. Floating bars show movement; totals start at zero.</text>')
    out.append("</svg></div>")
    return "".join(out)


def forecast_summary(ctx: Context) -> list[dict[str, object]]:
    p = ctx.manifest["pipeline"]
    return [
        {"label": f"{ctx.forecast_period} closed won", "count": sum(r["period"] == ctx.forecast_period and r["stage"] == "Closed Won" for r in ctx.closed_opps), "value": p["q4_closed_won_arr"], "color": TOKENS["dark"]},
        *[
            {"label": category, "count": sum(r["forecast_category"] == category for r in ctx.open_opps), "value": p["open_expected_arr_by_forecast"][category], "color": color}
            for category, color in zip(FORECAST_ORDER, [TOKENS["accent"], TOKENS["secondary"], TOKENS["warn"]])
        ],
    ]


def forecast_bars(ctx: Context) -> str:
    items = forecast_summary(ctx)
    return bar_list(
        [(str(item["label"]), float(item["value"]), f'{money(int(item["value"]))} · {fmt_int(int(item["count"]))} deals', str(item["color"])) for item in items],
        "Mutually exclusive forecast components by expected ARR",
    )


def activation_funnel(ctx: Context) -> str:
    a = ctx.manifest["activation"]
    steps = [
        ("Signed up", a["signups"], 1.0, TOKENS["accent"]),
        ("Activated", a["activated"], a["activation_rate"], TOKENS["secondary_ink"]),
        ("Retained at week 2", a["retained_w2"], a["overall_retention"], TOKENS["good_ink"]),
    ]
    out = [f'<div class="funnel" role="group" aria-label="Activation funnel: {fmt_int(a["signups"])} signups, {fmt_int(a["activated"])} activated, {fmt_int(a["retained_w2"])} retained at week 2">']
    for label, count, rate, color in steps:
        width = count / a["signups"] * 100
        out.append(
            f'<div class="funnel-step"><strong>{esc(label)}</strong><div class="funnel-track"><div class="funnel-fill" style="width:{width:.3f}%;background:{color}">{fmt_int(count)}</div></div><div class="funnel-value">{pct(rate)} of signups</div></div>'
        )
    out.append("</div>")
    return "".join(out)


def weekly_activity(ctx: Context) -> dict[str, object]:
    activities = ctx.rows["crm-activities.csv"]
    end = max(date.fromisoformat(row["activity_date"]) for row in activities)
    start = end - timedelta(days=6)
    prior_start = start - timedelta(days=7)
    prior_end = start - timedelta(days=1)
    current = [row for row in activities if start <= date.fromisoformat(row["activity_date"]) <= end]
    prior = [row for row in activities if prior_start <= date.fromisoformat(row["activity_date"]) <= prior_end]
    return {"start": start, "end": end, "prior_start": prior_start, "prior_end": prior_end, "current": current, "prior": prior}


def build_arr(ctx: Context) -> str:
    a = ctx.manifest["arr"]
    arr = ctx.rows["arr-rollforward.csv"]
    gains = a["new_arr"] + a["expansion_arr"]
    losses = a["contraction_arr"] + a["churn_arr"]
    content = [so_what(f'ARR moved from <strong>{money(a["starting_arr"])}</strong> to <strong>{money(a["ending_arr"])}</strong> in {esc(ctx.arr_period)}, a net increase of <strong>{money(a["net_arr_added"])}</strong>. New and expansion added {money(gains)}; contraction and churn removed {money(losses)}. The roll-forward reconciles to zero residual.')]
    content.append(kpis([
        ("Ending ARR", money(a["ending_arr"]), fmt_int(a["ending_active_customers"]) + " active customers"),
        ("Net ARR added", signed_money(a["net_arr_added"]), f'{pct(a["net_arr_added"] / a["starting_arr"])} of starting ARR'),
        ("Net revenue retention", pct(a["nrr"]), "Excludes new ARR"),
        ("Gross revenue retention", pct(a["grr"]), "After contraction and churn"),
    ]))
    content.append(section(1, "Every movement, reconciled", f'New ARR contributes {money(a["new_arr"])} across {fmt_int(a["movement_counts"]["New"])} accounts. Expansion contributes {money(a["expansion_arr"])} across {fmt_int(a["movement_counts"]["Expansion"])} accounts. Losses are shown as positive source fields and subtracted in the bridge.', waterfall_svg(ctx)))
    movement_rows = [
        ["Starting ARR", money(a["starting_arr"]), fmt_int(a["starting_active_customers"]), "Opening active accounts"],
        ["New", Raw(f'<span class="pos">+{money(a["new_arr"])}</span>'), fmt_int(a["movement_counts"]["New"]), "Accounts with zero starting ARR"],
        ["Expansion", Raw(f'<span class="pos">+{money(a["expansion_arr"])}</span>'), fmt_int(a["movement_counts"]["Expansion"]), "Positive existing-account movement"],
        ["Contraction", Raw(f'<span class="neg">-{money(a["contraction_arr"])}</span>'), fmt_int(a["movement_counts"]["Contraction"]), "Negative movement, account remains active"],
        ["Churn", Raw(f'<span class="neg">-{money(a["churn_arr"])}</span>'), fmt_int(a["movement_counts"]["Churn"]), "Ending ARR is zero"],
        ["Ending ARR", money(a["ending_arr"]), fmt_int(a["ending_active_customers"]), "Start + new + expansion - contraction - churn"],
    ]
    content.append(section(2, "The bridge in exact dollars", f'The ending balance is {money(a["ending_arr"])}. Active customers increase by {fmt_int(a["ending_active_customers"] - a["starting_active_customers"])}, from {fmt_int(a["starting_active_customers"])} to {fmt_int(a["ending_active_customers"])}.', table(["Movement", "ARR", "Accounts", "Definition"], movement_rows, numeric=[1, 2], caption=f'{esc(ctx.arr_period)} ARR roll-forward, USD')))
    accounts = ctx.accounts
    segment_rows = []
    for segment in sorted({row["segment"] for row in accounts.values()}):
        subset = [row for row in arr if accounts[row["account_id"]]["segment"] == segment]
        start, end = sum_field(subset, "starting_arr"), sum_field(subset, "ending_arr")
        segment_rows.append([segment, fmt_int(len(subset)), money(start), money(end), signed_money(end - start), pct((end - start) / start)])
    content.append(section(3, "Segment detail", "Segment net movement uses the same account rows as the waterfall. Percentages use each segment's starting ARR as the denominator.", table(["Segment", "ARR rows", "Starting ARR", "Ending ARR", "Net movement", "Net growth"], segment_rows, numeric=[1, 2, 3, 4, 5])))
    top_movements = sorted([row for row in arr if row["movement_category"] != "Flat"], key=lambda row: abs(integer(row, "ending_arr") - integer(row, "starting_arr")), reverse=True)[:12]
    detail_rows = []
    for row in top_movements:
        account = accounts[row["account_id"]]
        detail_rows.append([account["account_alias"], account["segment"], row["movement_category"], row["previous_plan_tier"] + " to " + row["current_plan_tier"], money(integer(row, "starting_arr")), signed_money(integer(row, "ending_arr") - integer(row, "starting_arr")), money(integer(row, "ending_arr"))])
    body = table(["Account", "Segment", "Movement", "Plan", "Starting ARR", "Change", "Ending ARR"], detail_rows, numeric=[4, 5, 6], caption=f'12 largest absolute account movements from {fmt_int(len(arr))} ARR rows')
    body += f'<p class="small muted">Source detail: {link("data/arr-rollforward.csv", "all ARR rows")} and {link("data/crm-accounts.csv", "account attributes")}.</p>'
    content.append(section(4, "Representative account movements", "These are the largest absolute changes, sorted from source values. Aliases preserve anonymity.", body))
    return page(title=f'{ctx.arr_period} ARR waterfall', subtitle='A zero-baseline bridge from opening ARR to ending ARR, with exact account movement detail.', period=ctx.arr_period, content="".join(content), generated_on=ctx.generated_on, sources=sources(ctx, ["arr-rollforward.csv", "crm-accounts.csv"]), logo=ctx.logo, validation_scope=f'All {fmt_int(len(arr))} ARR rows in the synthetic {ctx.arr_period} cohort', validation_checks=["Aggregate and row-level ARR bridges reconcile exactly", "NRR and GRR denominators exclude new ARR"])


def build_forecast(ctx: Context) -> str:
    p = ctx.manifest["pipeline"]
    open_opps = ctx.open_opps
    content = [so_what(f'The commit view is <strong>{money(p["commit_view"])}</strong>: {money(p["q4_closed_won_arr"])} already closed won plus {money(p["open_expected_arr_by_forecast"]["Commit"])} in Commit. Best Case and Pipeline remain separate, mutually exclusive categories. Full pipeline is <strong>{money(p["full_pipeline_view"])}</strong>, unweighted.')]
    content.append(kpis([
        ("Commit view", money(p["commit_view"]), "Closed won + Commit"),
        ("Best case view", money(p["best_case_view"]), "Commit view + Best Case"),
        ("Full pipeline view", money(p["full_pipeline_view"]), "Unweighted, all categories"),
        ("Open expected ARR", money(p["open_expected_arr_total"]), f'{fmt_int(p["open_deals"])} open deals'),
    ]))
    content.append(section(1, "Forecast components stay exclusive", f'Each open deal appears in exactly one forecast category. The {fmt_int(p["open_deals"])} open deals carry {money(p["open_expected_arr_total"])} of expected ARR before any scenario layering. No probability weighting is applied.', f'<div class="card">{forecast_bars(ctx)}</div>'))
    scenario_rows = [
        [f"{ctx.forecast_period} closed won", fmt_int(forecast_summary(ctx)[0]["count"]), money(p["q4_closed_won_arr"]), money(p["q4_closed_won_arr"]), "Closed Won only"],
        ["Commit view", fmt_int(p["open_by_forecast"]["Commit"]), money(p["open_expected_arr_by_forecast"]["Commit"]), money(p["commit_view"]), "Closed won + Commit"],
        ["Best case view", fmt_int(p["open_by_forecast"]["Best Case"]), money(p["open_expected_arr_by_forecast"]["Best Case"]), money(p["best_case_view"]), "Commit view + Best Case"],
        ["Full pipeline view", fmt_int(p["open_by_forecast"]["Pipeline"]), money(p["open_expected_arr_by_forecast"]["Pipeline"]), money(p["full_pipeline_view"]), "Best case view + Pipeline, unweighted"],
    ]
    content.append(section(2, "Scenario arithmetic", "The deal count column shows only the component added at that step. The cumulative view adds that component to the prior view, so no deal is counted twice.", table(["View", "Added open deals", "Added expected ARR", "Cumulative expected ARR", "Rule"], scenario_rows, numeric=[1, 2, 3], caption=f'{esc(ctx.forecast_period)} forecast scenarios, USD, not probability weighted')))
    stage_rows = []
    for stage in STAGE_ORDER:
        subset = [row for row in open_opps if row["stage"] == stage]
        stage_rows.append([stage, fmt_int(len(subset)), money(sum_field(subset, "expected_arr_usd")), pct(sum(integer(row, "probability") for row in subset) / len(subset) / 100), ", ".join(f'{cat}: {sum(row["forecast_category"] == cat for row in subset)}' for cat in FORECAST_ORDER)])
    content.append(section(3, "Stage and category cross-check", "Average probability is descriptive only. It is not used in the scenario views above. Discovery and Validation sit entirely in Pipeline in this snapshot.", table(["Stage", "Open deals", "Expected ARR", "Average probability", "Forecast mix"], stage_rows, numeric=[1, 2, 3])))
    owner_rows = []
    for owner in sorted({row["owner_alias"] for row in open_opps}):
        subset = [row for row in open_opps if row["owner_alias"] == owner]
        owner_rows.append([owner, fmt_int(len(subset)), money(sum_field(subset, "expected_arr_usd")), money(sum(integer(row, "expected_arr_usd") for row in subset if row["forecast_category"] == "Commit")), fmt_int(sum(row["risk_status"] == "At risk" for row in subset)), money(max(integer(row, "expected_arr_usd") for row in subset))])
    content.append(section(4, "Owner coverage", f'Open expected ARR and at-risk counts reconcile to the same {fmt_int(len(open_opps))}-deal population. Use the pipeline analysis for row-level follow-up.', table(["Owner", "Open deals", "Expected ARR", "Commit ARR", "At-risk deals", "Largest deal"], owner_rows, numeric=[1, 2, 3, 4, 5]) + f'<p class="small muted">Next: {link("tour/pipeline-analysis.html", "inspect every open deal")}.</p>'))
    return page(title=f'{ctx.forecast_period} revenue forecast', subtitle='Closed-won ARR and three exclusive open-pipeline categories, with explicit scenario math.', period=ctx.forecast_period, content="".join(content), generated_on=ctx.generated_on, sources=sources(ctx, ["crm-opportunities.csv", "mock-pipeline.csv"]), logo=ctx.logo, validation_scope=f'All {fmt_int(len(open_opps))} open and {fmt_int(len(ctx.closed_opps))} closed synthetic opportunities', validation_checks=["Forecast categories are mutually exclusive", "Full pipeline is unweighted expected ARR"])


def build_activation(ctx: Context) -> str:
    a = ctx.manifest["activation"]
    rows = ctx.rows["activation-users.csv"]
    content = [so_what(f'<strong>{fmt_int(a["activated"])}</strong> of {fmt_int(a["signups"])} signups activated, a rate of <strong>{pct(a["activation_rate"])}</strong>. {fmt_int(a["retained_w2"])} activated users remained at week 2, which is {pct(a["retention_of_activated"])} of activated users and {pct(a["overall_retention"])} of all signups.')]
    content.append(kpis([
        ("Signups", fmt_int(a["signups"]), f'{len(a["cohorts"])} weekly cohorts'),
        ("Activated", fmt_int(a["activated"]), pct(a["activation_rate"]) + " of signups"),
        ("Retained at week 2", fmt_int(a["retained_w2"]), pct(a["retention_of_activated"]) + " of activated"),
        ("Overall week-2 retention", pct(a["overall_retention"]), "Retained / all signups"),
    ]))
    content.append(section(1, "Signup to week-two retention", "Activation and retention are user-level flags in the source. Every retained user is also activated. Retention is not a revenue metric.", f'<div class="card">{activation_funnel(ctx)}</div>'))
    cohort_rows = []
    for cohort in sorted(a["cohorts"]):
        values = a["cohorts"][cohort]
        cohort_rows.append([cohort, fmt_int(values["signups"]), fmt_int(values["activated"]), pct(values["activated"] / values["signups"]), fmt_int(values["retained_w2"]), pct(values["retained_w2"] / values["activated"]), pct(values["retained_w2"] / values["signups"])])
    content.append(section(2, "Weekly cohort detail", "Rates are calculated within each cohort. Cohorts have similar but not equal signup counts, so counts and rates are shown together.", table(["Cohort", "Signups", "Activated", "Activation rate", "Retained W2", "Retention of activated", "Overall retention"], cohort_rows, numeric=[1, 2, 3, 4, 5, 6])))
    source_rows = []
    for acquisition in sorted({row["acquisition_source"] for row in rows}):
        subset = [row for row in rows if row["acquisition_source"] == acquisition]
        activated = sum(row["activated"] == "true" for row in subset)
        retained = sum(row["retained_w2"] == "true" for row in subset)
        source_rows.append([acquisition, fmt_int(len(subset)), fmt_int(activated), pct(activated / len(subset)), fmt_int(retained), pct(retained / activated), pct(retained / len(subset))])
    content.append(section(3, "Acquisition source mix", "This synthetic snapshot describes observed source-level rates. It does not establish that acquisition source caused activation or retention.", table(["Source", "Signups", "Activated", "Activation rate", "Retained W2", "Retention of activated", "Overall retention"], source_rows, numeric=[1, 2, 3, 4, 5, 6])))
    recent = sorted(rows, key=lambda row: (row["signup_date"], row["user_alias"]), reverse=True)[:12]
    account_map = ctx.accounts
    detail = [[row["user_alias"], account_map[row["account_id"]]["account_alias"], row["cohort_week"], row["signup_date"], badge("Activated", "secondary") if row["activated"] == "true" else badge("Not activated"), badge("Retained W2", "good") if row["retained_w2"] == "true" else badge("Not retained"), row["acquisition_source"]] for row in recent]
    content.append(section(4, "Representative user rows", "The latest 12 signups by date and alias show the exact flags behind the funnel. Internal user and account IDs are not displayed.", table(["User", "Account", "Cohort", "Signup", "Activation", "Week-2 retention", "Source"], detail, caption=f'12 representative rows from {fmt_int(len(rows))} synthetic users') + f'<p class="small muted">{link("data/activation-users.csv", "Open the full activation CSV")}.</p>'))
    return page(title="Activation funnel", subtitle='User-level signup, activation and week-two retention across four weekly cohorts.', period=f'{min(a["cohorts"])} to {max(a["cohorts"])}', content="".join(content), generated_on=ctx.generated_on, sources=sources(ctx, ["activation-users.csv", "crm-accounts.csv"]), logo=ctx.logo, validation_scope=f'All {fmt_int(len(rows))} synthetic activation users; complete cohort coverage', validation_checks=["Retained users are a subset of activated users", "Both activated-user and all-signup retention denominators are labeled"])


def build_weekly(ctx: Context) -> str:
    w = weekly_activity(ctx)
    current, prior = w["current"], w["prior"]
    assert isinstance(current, list) and isinstance(prior, list)
    start, end = w["start"], w["end"]
    assert isinstance(start, date) and isinstance(end, date)
    delta = (len(current) - len(prior)) / len(prior)
    completed = sum(row["outcome"] == "Completed" for row in current)
    meetings = sum(row["activity_type"] == "Meeting" for row in current)
    owners_active = len({row["owner_id"] for row in current})
    period = f'{start.isoformat()} to {end.isoformat()}'
    content = [so_what(f'The latest seven-day window contains <strong>{fmt_int(len(current))} activities</strong>, {pct(delta)} versus the prior seven days. {fmt_int(completed)} are marked Completed. These counts describe CRM logging, not rep productivity or revenue outcomes.')]
    content.append(kpis([
        ("Logged activities", fmt_int(len(current)), f'{signed_money(len(current)-len(prior)).replace("$", "")} vs prior window'),
        ("Completed", fmt_int(completed), pct(completed / len(current)) + " of current window"),
        ("Meetings", fmt_int(meetings), pct(meetings / len(current)) + " of current window"),
        ("Active owners", fmt_int(owners_active), "Owners with at least one activity"),
    ]))
    type_rows = []
    for activity_type in sorted({row["activity_type"] for row in current + prior}):
        now = sum(row["activity_type"] == activity_type for row in current)
        before = sum(row["activity_type"] == activity_type for row in prior)
        completed_now = sum(row["activity_type"] == activity_type and row["outcome"] == "Completed" for row in current)
        type_rows.append([activity_type, fmt_int(now), fmt_int(before), fmt_int(now - before), pct(now / len(current)), pct(completed_now / completed) if completed else "0.0%"])
    content.append(section(1, "Activity mix", f'Window: {start.isoformat()} through {end.isoformat()}. Prior window: {w["prior_start"].isoformat()} through {w["prior_end"].isoformat()}. Share of completed counts only Completed activities of each type and uses all Completed activities as its denominator.', table(["Type", "Current", "Prior", "Change", "Share of current", "Share of completed"], type_rows, numeric=[1, 2, 3, 4, 5])))
    owner_rows = []
    owner_names = ctx.owner_names
    for owner_id in sorted({row["owner_id"] for row in current + prior}, key=lambda item: owner_names[item]):
        now_rows = [row for row in current if row["owner_id"] == owner_id]
        before = sum(row["owner_id"] == owner_id for row in prior)
        owner_rows.append([owner_names[owner_id], fmt_int(len(now_rows)), fmt_int(before), fmt_int(len(now_rows) - before), fmt_int(sum(row["outcome"] == "Completed" for row in now_rows)), fmt_int(sum(row["activity_type"] == "Meeting" for row in now_rows)), fmt_int(sum(row["outcome"] == "No Response" for row in now_rows))])
    content.append(section(2, "Owner activity", "Owner aliases come from the quota owner map and join by owner ID internally. Counts are presented without interpreting them as performance rankings.", table(["Owner", "Current", "Prior", "Change", "Completed", "Meetings", "No response"], owner_rows, numeric=[1, 2, 3, 4, 5, 6])))
    outcome_rows = []
    for outcome in sorted({row["outcome"] for row in current + prior}):
        now = sum(row["outcome"] == outcome for row in current)
        before = sum(row["outcome"] == outcome for row in prior)
        outcome_rows.append([outcome, fmt_int(now), fmt_int(before), fmt_int(now - before), pct(now / len(current))])
    content.append(section(3, "Outcome fields", "Scheduled and No Response are source outcomes, not inferred engagement measures. No cross-channel activity outside this CRM file is claimed.", table(["Outcome", "Current", "Prior", "Change", "Current share"], outcome_rows, numeric=[1, 2, 3, 4])))
    accounts = ctx.accounts
    opp_map = {row["opportunity_id"]: row for row in ctx.rows["crm-opportunities.csv"]}
    recent = sorted(current, key=lambda row: (row["activity_date"], row["subject_alias"]), reverse=True)[:15]
    details = [[row["activity_date"], accounts[row["account_id"]]["account_alias"], opp_map[row["opportunity_id"]]["opportunity_alias"], owner_names[row["owner_id"]], row["activity_type"], row["outcome"]] for row in recent]
    content.append(section(4, "Recent row detail", "The latest 15 activity rows in the current window resolve to human-readable account, opportunity and owner aliases.", table(["Date", "Account", "Opportunity", "Owner", "Type", "Outcome"], details, caption=f'15 rows from {fmt_int(len(current))} current-window activities') + f'<p class="small muted">{link("data/crm-activities.csv", "Open all activity rows")}.</p>'))
    return page(title="Weekly activity recap", subtitle='A seven-day CRM activity summary with a matched prior window and owner-level detail.', period=period, content="".join(content), generated_on=ctx.generated_on, sources=sources(ctx, ["crm-activities.csv", "crm-opportunities.csv", "crm-accounts.csv", "quota-targets.csv"]), logo=ctx.logo, validation_scope=f'All {fmt_int(len(current))} current-window and {fmt_int(len(prior))} prior-window synthetic CRM activities', validation_checks=["Current and prior windows are both seven days", "Activity volume is not interpreted as a causal outcome"])


def build_briefing(ctx: Context) -> str:
    a, p = ctx.manifest["arr"], ctx.manifest["pipeline"]
    w = weekly_activity(ctx)
    current, prior = w["current"], w["prior"]
    assert isinstance(current, list) and isinstance(prior, list)
    delta = (len(current) - len(prior)) / len(prior)
    at_risk_commit = sorted([row for row in ctx.open_opps if row["risk_status"] == "At risk" and row["forecast_category"] == "Commit"], key=lambda row: (row["close_date"], -integer(row, "expected_arr_usd")))
    risk_value = sum_field(at_risk_commit, "expected_arr_usd")
    activation = ctx.manifest["activation"]
    top = at_risk_commit[:5]
    risk_rows = [[row["opportunity_alias"], row["owner_alias"], row["stage"], money(integer(row, "expected_arr_usd")), row["close_date"], row["next_step_date"]] for row in top]
    content = [f'''<div class="email-shell">
<div class="email-head"><dl><dt>From</dt><dd>Vera, RevOps teammate</dd><dt>To</dt><dd>Northwind revenue leadership</dd><dt>Subject</dt><dd><strong>{esc(ctx.forecast_period)} brief: {money(a["ending_arr"])} ARR and {money(p["commit_view"])} commit view</strong></dd><dt>Data</dt><dd>Synthetic / anonymized snapshot generated {esc(ctx.generated_on)}</dd></dl></div>
<div class="email-body">
<p>Hi team,</p>
<p>Three numbers for today: ending ARR is <strong>{money(a["ending_arr"])}</strong>, the commit view is <strong>{money(p["commit_view"])}</strong>, and {fmt_int(len(current))} CRM activities were logged in the latest seven-day window.</p>
<section><h2>1. ARR base</h2><p>{esc(ctx.arr_period)} added {money(a["net_arr_added"])} net ARR. NRR is {pct(a["nrr"])} and GRR is {pct(a["grr"])}. Churn removed {money(a["churn_arr"])} across {fmt_int(a["movement_counts"]["Churn"])} accounts; contraction removed {money(a["contraction_arr"])} across {fmt_int(a["movement_counts"]["Contraction"])}.</p></section>
<section><h2>2. Forecast</h2><p>The commit view combines {money(p["q4_closed_won_arr"])} of {esc(ctx.forecast_period)} closed-won expected ARR with {money(p["open_expected_arr_by_forecast"]["Commit"])} in Commit. Adding Best Case gives {money(p["best_case_view"])}. Full pipeline is {money(p["full_pipeline_view"])}, unweighted.</p></section>
<section><h2>3. Activity and activation</h2><p>Activity volume moved {pct(delta)} versus the prior seven days. This is a logging summary, not a performance judgment. Separately, {fmt_int(activation["activated"])} of {fmt_int(activation["signups"])} synthetic signups activated ({pct(activation["activation_rate"])}), and {fmt_int(activation["retained_w2"])} remained at week 2.</p></section>
<section><h2>4. Needs review</h2><p>{fmt_int(len(at_risk_commit))} Commit deals are marked At risk, carrying {money(risk_value)} of expected ARR. The five below are ordered by close date, then value. Review the next step before treating the category as a commitment.</p>{table(["Deal", "Owner", "Stage", "Expected ARR", "Close", "Next step"], risk_rows, numeric=[3], classes="compact")}</section>
<p>Full evidence is in the linked HTML examples and source CSVs. No live CRM connection was used.</p>
<p>Best,<br>Vera</p>
</div></div>''']
    return page(title="Revenue briefing email", subtitle='A ready-to-review email brief assembled from the same ARR, pipeline, activation and activity rows.', period=f'{ctx.arr_period} and {ctx.forecast_period}', content="".join(content), generated_on=ctx.generated_on, sources=sources(ctx, ["arr-rollforward.csv", "crm-opportunities.csv", "crm-activities.csv", "activation-users.csv"]), logo=ctx.logo, validation_scope=f'Full synthetic ARR, forecast and activation cohorts plus {fmt_int(len(current))} current-window activities', validation_checks=["Email headline values match the ARR and forecast manifests", "At-risk Commit list is filtered on both fields"])


def build_slides(ctx: Context) -> str:
    a, p, act = ctx.manifest["arr"], ctx.manifest["pipeline"], ctx.manifest["activation"]
    open_opps = ctx.open_opps
    at_risk = [row for row in open_opps if row["risk_status"] == "At risk"]
    stage_items = [(stage, sum(row["stage"] == stage for row in open_opps), fmt_int(sum(row["stage"] == stage for row in open_opps)) + " deals", TOKENS["accent"]) for stage in STAGE_ORDER]
    risk_rows = [[row["opportunity_alias"], row["owner_alias"], row["forecast_category"], money(integer(row, "expected_arr_usd")), row["close_date"]] for row in sorted(at_risk, key=lambda row: integer(row, "expected_arr_usd"), reverse=True)[:6]]
    slides = []
    slides.append(f'<article class="slide dark" id="slide-1" data-slide="1"><p class="eyebrow">Northwind revenue review</p><h2>{esc(ctx.arr_period)} ARR and {esc(ctx.forecast_period)} outlook</h2><p class="takeaway">A browser companion generated from the synthetic source CSVs. Use arrow keys or the controls to move between slides.</p>{kpis([("Ending ARR", money(a["ending_arr"]), fmt_int(a["ending_active_customers"]) + " active customers"), ("Net ARR added", signed_money(a["net_arr_added"]), pct(a["net_arr_added"]/a["starting_arr"]) + " of start"), ("Commit view", money(p["commit_view"]), "Closed won + Commit"), ("Open deals", fmt_int(p["open_deals"]), money(p["open_expected_arr_total"]) + " expected ARR")])}</article>')
    slides.append(f'<article class="slide" id="slide-2" data-slide="2"><p class="eyebrow">1. ARR movement</p><h2>Growth reconciles to {money(a["ending_arr"])}</h2><p class="takeaway">New and expansion add {money(a["new_arr"] + a["expansion_arr"])}. Contraction and churn subtract {money(a["contraction_arr"] + a["churn_arr"])}. NRR is {pct(a["nrr"])}.</p>{waterfall_svg(ctx, "slide-arr")}</article>')
    slides.append(f'<article class="slide" id="slide-3" data-slide="3"><p class="eyebrow">2. Forecast</p><h2>Commit is a layer, not the whole pipeline</h2><p class="takeaway">Closed won {money(p["q4_closed_won_arr"])} + Commit {money(p["open_expected_arr_by_forecast"]["Commit"])} = {money(p["commit_view"])}. Best case view is {money(p["best_case_view"])}. Full pipeline is {money(p["full_pipeline_view"])}, unweighted.</p><div class="card">{forecast_bars(ctx)}</div></article>')
    slides.append(f'<article class="slide" id="slide-4" data-slide="4"><p class="eyebrow">3. Activation</p><h2>{pct(act["activation_rate"])} of signups activate</h2><p class="takeaway">{fmt_int(act["activated"])} of {fmt_int(act["signups"])} activate. {fmt_int(act["retained_w2"])} remain at week 2, or {pct(act["retention_of_activated"])} of activated users.</p>{activation_funnel(ctx)}</article>')
    slides.append(f'<article class="slide" id="slide-5" data-slide="5"><p class="eyebrow">4. Pipeline motion and risk</p><h2>{fmt_int(len(at_risk))} open deals are marked At risk</h2><p class="takeaway">They carry {money(sum_field(at_risk, "expected_arr_usd"))} of expected ARR. Stage counts sum to {fmt_int(len(open_opps))}; risk is a separate source field.</p><div class="grid-2"><div class="card">{bar_list(stage_items, "Open deals by stage")}</div><div>{table(["Deal", "Owner", "Forecast", "Expected ARR", "Close"], risk_rows, numeric=[3], classes="compact", caption="Six largest at-risk open deals")}</div></div></article>')
    slides.append(f'<article class="slide dark" id="slide-6" data-slide="6"><p class="eyebrow">5. Review path</p><h2>Inspect the rows behind each number</h2><div class="stack"><div class="callout"><h3>Protect the commit view</h3><p>Review the at-risk Commit deals and their next-step dates. Do not replace category logic with probability weighting.</p></div><div class="callout"><h3>Read retention with its denominator</h3><p>Week-two retention is {pct(act["retention_of_activated"])} of activated users and {pct(act["overall_retention"])} of all signups.</p></div><div class="callout"><h3>Use the source files for follow-through</h3><p>Every chart in this companion is reproducible from the linked CSVs. Office rendering is handled separately.</p></div></div></article>')
    nav = '<div class="slide-nav no-print"><div><button type="button" id="slide-prev" aria-label="Previous slide">Previous</button> <button type="button" id="slide-next" aria-label="Next slide">Next</button></div><span class="slide-count" id="slide-count" aria-live="polite">Slide 1 of 6</span></div>'
    intro = so_what(f'This six-slide browser companion uses the same validated snapshot as the reports. Headline ARR is <strong>{money(a["ending_arr"])}</strong>; headline commit view is <strong>{money(p["commit_view"])}</strong>.')
    script = r"""
(function(){
  const slides=Array.from(document.querySelectorAll('[data-slide]'));
  const count=document.getElementById('slide-count');
  let current=0;
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function show(index){
    current=Math.max(0,Math.min(slides.length-1,index));
    count.textContent='Slide '+(current+1)+' of '+slides.length;
    slides[current].scrollIntoView({behavior:reduced?'auto':'smooth',block:'start'});
  }
  document.getElementById('slide-prev').addEventListener('click',function(){show(current-1);});
  document.getElementById('slide-next').addEventListener('click',function(){show(current+1);});
  document.addEventListener('keydown',function(event){
    if(['INPUT','SELECT','TEXTAREA'].includes(document.activeElement.tagName))return;
    if(event.key==='ArrowRight'||event.key==='PageDown'){event.preventDefault();show(current+1);}
    if(event.key==='ArrowLeft'||event.key==='PageUp'){event.preventDefault();show(current-1);}
  });
  const observer=new IntersectionObserver(function(entries){
    entries.forEach(function(entry){if(entry.isIntersecting){current=slides.indexOf(entry.target);count.textContent='Slide '+(current+1)+' of '+slides.length;}});
  },{threshold:.55});
  slides.forEach(function(slide){observer.observe(slide);});
})();
"""
    return page(title="Revenue review slides", subtitle='Six browser slides for ARR, forecast, activation and open-pipeline risk. Keyboard and print friendly.', period=f'{ctx.arr_period} and {ctx.forecast_period}', content=intro + nav + '<div class="slides">' + "".join(slides) + "</div>", generated_on=ctx.generated_on, sources=sources(ctx, ["arr-rollforward.csv", "crm-opportunities.csv", "activation-users.csv"]), logo=ctx.logo, script=script, validation_scope=f'Complete synthetic ARR, forecast and activation cohorts; {fmt_int(len(open_opps))} open opportunities', validation_checks=["Slide headlines reuse validated report metrics", "Reduced motion disables smooth scrolling"])

def build_dashboard(ctx: Context) -> str:
    a, p = ctx.manifest["arr"], ctx.manifest["pipeline"]
    open_opps = ctx.open_opps
    at_risk = [row for row in open_opps if row["risk_status"] == "At risk"]
    content = [so_what(f'The revenue base ends {esc(ctx.arr_period)} at <strong>{money(a["ending_arr"])}</strong>, with {pct(a["nrr"])} NRR. The {esc(ctx.forecast_period)} commit view is <strong>{money(p["commit_view"])}</strong>. {fmt_int(len(at_risk))} open deals marked At risk carry {money(sum_field(at_risk, "expected_arr_usd"))} of unweighted expected ARR.')]
    content.append(kpis([
        ("Ending ARR", money(a["ending_arr"]), fmt_int(a["ending_active_customers"]) + " active customers"),
        ("Net revenue retention", pct(a["nrr"]), "Expansion net of losses, excluding new"),
        ("Commit view", money(p["commit_view"]), f"{ctx.forecast_period} closed won + Commit"),
        ("Open expected ARR", money(p["open_expected_arr_total"]), f'{fmt_int(len(open_opps))} open deals, unweighted'),
    ]))
    content.append(section(1, "ARR bridge", f'{money(a["net_arr_added"])} of net ARR was added. The zero-baseline chart preserves the scale of gains and losses against the full revenue base.', waterfall_svg(ctx, "dashboard-arr")))
    content.append(section(2, "Forecast layers", f'Closed won, Commit, Best Case and Pipeline are separate components. The full pipeline view is {money(p["full_pipeline_view"])} and is not probability weighted.', f'<div class="grid-2"><div class="card">{forecast_bars(ctx)}</div><div class="card"><h3>Scenario views</h3>{bar_list([("Commit view", p["commit_view"], money(p["commit_view"]), TOKENS["accent"]), ("Best case view", p["best_case_view"], money(p["best_case_view"]), TOKENS["secondary"]), ("Full pipeline view", p["full_pipeline_view"], money(p["full_pipeline_view"]), TOKENS["dark"])], "Cumulative forecast scenario views")}<p class="chart-note">Each view adds the named exclusive category to the prior view.</p></div></div>'))
    stage_rows = []
    for stage in STAGE_ORDER:
        subset = [row for row in open_opps if row["stage"] == stage]
        stage_rows.append([stage, fmt_int(len(subset)), money(sum_field(subset, "expected_arr_usd")), fmt_int(sum(row["risk_status"] == "At risk" for row in subset)), fmt_int(sum(row["forecast_category"] == "Commit" for row in subset))])
    risk_rows = []
    for risk in RISK_ORDER:
        subset = [row for row in open_opps if row["risk_status"] == risk]
        risk_rows.append([risk_badge(risk), fmt_int(len(subset)), money(sum_field(subset, "expected_arr_usd")), pct(len(subset) / len(open_opps)), money(sum(integer(row, "expected_arr_usd") for row in subset if row["forecast_category"] == "Commit"))])
    content.append(section(3, "Stage and risk readout", "Risk is reported independently from stage and forecast category. At-risk expected ARR is not removed from the forecast views; it is a review queue.", f'<div class="grid-2"><div>{table(["Stage", "Deals", "Expected ARR", "At risk", "Commit"], stage_rows, numeric=[1, 2, 3, 4], classes="compact")}</div><div>{table(["Risk", "Deals", "Expected ARR", "Deal share", "Commit ARR"], risk_rows, numeric=[1, 2, 3, 4], classes="compact")}</div></div>'))
    owner_rows = []
    for owner in sorted({row["owner_alias"] for row in open_opps}):
        subset = [row for row in open_opps if row["owner_alias"] == owner]
        risky = [row for row in subset if row["risk_status"] == "At risk"]
        owner_rows.append([owner, fmt_int(len(subset)), money(sum_field(subset, "expected_arr_usd")), money(sum(integer(row, "expected_arr_usd") for row in subset if row["forecast_category"] == "Commit")), fmt_int(len(risky)), money(sum_field(risky, "expected_arr_usd"))])
    content.append(section(4, "Owner action queue", "Owners are sorted by alias. At-risk ARR gives the review queue a value without changing the underlying forecast category.", table(["Owner", "Open deals", "Expected ARR", "Commit ARR", "At-risk deals", "At-risk ARR"], owner_rows, numeric=[1, 2, 3, 4, 5]) + f'<p class="small muted">Continue to {link("pipeline-analysis.html", "pipeline analysis")} or {link("../mock-arr-waterfall.html", "the full ARR waterfall")}.</p>'))
    return page(title="Revenue dashboard", subtitle='One combined view of ARR movement, forecast layers, open-pipeline stage and owner risk.', period=f'{ctx.arr_period} and {ctx.forecast_period}', content="".join(content), generated_on=ctx.generated_on, sources=sources(ctx, ["arr-rollforward.csv", "crm-opportunities.csv"], depth=1), logo=ctx.logo, depth=1, validation_scope=f'All {fmt_int(len(ctx.rows["arr-rollforward.csv"]))} ARR rows and {fmt_int(len(open_opps))} open opportunities', validation_checks=["Dashboard ARR and forecast headlines match standalone reports", "Risk overlays do not alter unweighted forecast categories"])


def pipeline_motion_svg(ctx: Context) -> str:
    open_opps = ctx.open_opps
    width, height = 960, 460
    stage_y = {stage: 85 + index * 100 for index, stage in enumerate(STAGE_ORDER)}
    forecast_y = {category: 125 + index * 125 for index, category in enumerate(FORECAST_ORDER)}
    out = ['<div class="chart-scroll" id="pipeline-map-wrap"><svg class="motion-map" viewBox="0 0 960 460" role="img" aria-labelledby="motion-title motion-desc">']
    out.append(f'<title id="motion-title">Current stage to forecast category mapping for {fmt_int(len(open_opps))} open opportunities</title>')
    out.append(f'<desc id="motion-desc">Animated paths connect each current stage to its forecast categories. Path width represents deal count. The mapping contains {fmt_int(len(open_opps))} deals and does not imply historical conversion.</desc>')
    for stage in STAGE_ORDER:
        for category in FORECAST_ORDER:
            count = sum(row["stage"] == stage and row["forecast_category"] == category for row in open_opps)
            if not count:
                continue
            y1, y2 = stage_y[stage], forecast_y[category]
            path = f'M 255 {y1} C 420 {y1}, 520 {y2}, 690 {y2}'
            color_class = " secondary" if category == "Best Case" else ""
            out.append(f'<path class="motion-path{color_class}" d="{path}" stroke-width="{2 + count * .42:.2f}"><title>{esc(stage)} to {esc(category)}: {count} deals</title></path>')
    for stage in STAGE_ORDER:
        subset = [row for row in open_opps if row["stage"] == stage]
        y = stage_y[stage]
        out.append(f'<rect x="25" y="{y-31}" width="230" height="62" rx="10" fill="{TOKENS["surface"]}" stroke="{TOKENS["line"]}"/>')
        out.append(f'<text x="45" y="{y-3}" font-size="15" font-weight="700" fill="{TOKENS["ink"]}">{esc(stage)}</text><text x="45" y="{y+19}" font-size="12" fill="{TOKENS["muted"]}">{len(subset)} deals · {esc(compact_money(sum_field(subset, "expected_arr_usd")))}</text>')
    for category in FORECAST_ORDER:
        subset = [row for row in open_opps if row["forecast_category"] == category]
        y = forecast_y[category]
        fill = {"Commit": TOKENS["good_soft"], "Best Case": TOKENS["secondary_soft"], "Pipeline": TOKENS["warn_soft"]}[category]
        out.append(f'<rect x="690" y="{y-36}" width="240" height="72" rx="10" fill="{fill}" stroke="{TOKENS["line"]}"/>')
        out.append(f'<text x="712" y="{y-4}" font-size="15" font-weight="700" fill="{TOKENS["ink"]}">{esc(category)}</text><text x="712" y="{y+20}" font-size="12" fill="{TOKENS["muted"]}">{len(subset)} deals · {esc(compact_money(sum_field(subset, "expected_arr_usd")))}</text>')
    out.append(f'<text x="25" y="28" font-size="13" font-weight="700" fill="{TOKENS["ink"]}">Current stage</text><text x="690" y="28" font-size="13" font-weight="700" fill="{TOKENS["ink"]}">Exclusive forecast category</text>')
    out.append(f'<text x="25" y="445" font-size="12" fill="{TOKENS["muted"]}">Paths show current record mappings, not deal conversion over time.</text></svg></div>')
    return "".join(out)


def build_pipeline_motion(ctx: Context) -> str:
    open_opps = ctx.open_opps
    content = [so_what(f'All <strong>{fmt_int(len(open_opps))} open deals</strong> map from one current stage to exactly one forecast category. Motion makes the mapping easier to scan; it does not claim stage conversion or deal velocity. Pause and static controls are provided.')]
    content.append(kpis([
        ("Open deals", fmt_int(len(open_opps)), "One stage and one forecast each"),
        ("Expected ARR", money(sum_field(open_opps, "expected_arr_usd")), "Unweighted"),
        ("Stage groups", fmt_int(len(STAGE_ORDER)), "Discovery through Negotiation"),
        ("Forecast groups", fmt_int(len(FORECAST_ORDER)), "Mutually exclusive"),
    ]))
    controls = '<div class="controls no-print"><button type="button" id="motion-toggle" aria-pressed="false">Pause motion</button><button type="button" id="static-toggle" aria-pressed="false">Use static view</button><span class="small muted" id="motion-status" aria-live="polite">Motion is on unless reduced motion is preferred.</span></div>'
    content.append(section(1, "Stage to forecast map", "Line width represents the number of current records at each intersection. Values are repeated in the matrix below for nonvisual review.", controls + pipeline_motion_svg(ctx)))
    matrix_rows = []
    for stage in STAGE_ORDER:
        subset = [row for row in open_opps if row["stage"] == stage]
        matrix_rows.append([stage, *[fmt_int(sum(row["forecast_category"] == category for row in subset)) for category in FORECAST_ORDER], fmt_int(len(subset)), money(sum_field(subset, "expected_arr_usd"))])
    matrix_rows.append(["Total", *[fmt_int(sum(row["forecast_category"] == category for row in open_opps)) for category in FORECAST_ORDER], fmt_int(len(open_opps)), money(sum_field(open_opps, "expected_arr_usd"))])
    content.append(section(2, "Accessible count matrix", f'Rows sum to stage totals and columns sum to forecast totals. The grand total is the full {fmt_int(len(open_opps))}-deal open population.', table(["Current stage", *FORECAST_ORDER, "Total deals", "Expected ARR"], matrix_rows, numeric=[1, 2, 3, 4, 5])))
    history = ctx.rows["crm-stage-history.csv"]
    open_ids = {row["opportunity_id"] for row in open_opps}
    open_history = [row for row in history if row["opportunity_id"] in open_ids]
    history_rows = []
    for stage in STAGE_ORDER:
        subset = [row for row in open_history if row["stage"] == stage]
        history_rows.append([stage, fmt_int(len(subset)), fmt_int(len({row["opportunity_id"] for row in subset})), fmt_int(sum(not row["exited_at"] for row in subset)), "Current open-deal history only"])
    content.append(section(3, "What the motion does not mean", f'The map is a current-state cross-tab. Stage history contains {fmt_int(len(open_history))} rows for these open opportunities, but this visual does not infer conversion rates from those records.', table(["Stage", "History rows", "Deals present", "Unexited rows", "Scope"], history_rows, numeric=[1, 2, 3], classes="compact") + '<div class="callout warn" style="margin-top:14px"><p>Reduced-motion preferences remove animation automatically. The static button removes dashed movement for everyone else.</p></div>'))
    script = r"""
(function(){
  const wrap=document.getElementById('pipeline-map-wrap');
  const motion=document.getElementById('motion-toggle');
  const staticButton=document.getElementById('static-toggle');
  const status=document.getElementById('motion-status');
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)');
  let paused=reduced.matches;
  let isStatic=false;
  function render(){
    wrap.classList.toggle('motion-paused',paused);
    wrap.classList.toggle('static-view',isStatic);
    motion.setAttribute('aria-pressed',String(paused));
    staticButton.setAttribute('aria-pressed',String(isStatic));
    motion.textContent=paused?'Resume motion':'Pause motion';
    staticButton.textContent=isStatic?'Use animated view':'Use static view';
    status.textContent=isStatic?'Static view is on.':(paused?'Motion is paused.':'Motion is on.');
  }
  motion.addEventListener('click',function(){paused=!paused;if(!paused)isStatic=false;render();});
  staticButton.addEventListener('click',function(){isStatic=!isStatic;render();});
  reduced.addEventListener('change',function(event){if(event.matches){paused=true;render();}});
  render();
})();
"""
    return page(title="Pipeline motion map", subtitle='An animated current-stage to forecast-category map with pause, static and reduced-motion states.', period=ctx.forecast_period, content="".join(content), generated_on=ctx.generated_on, sources=sources(ctx, ["crm-opportunities.csv", "crm-stage-history.csv"], depth=1), logo=ctx.logo, depth=1, script=script, validation_scope=f'All {fmt_int(len(open_opps))} open deals and their {fmt_int(len(open_history))} stage-history rows', validation_checks=[f'Stage by forecast matrix reconciles to {fmt_int(len(open_opps))} open deals', "Animation is not interpreted as conversion evidence"])


def build_campaign(ctx: Context) -> str:
    expansion = [row for row in ctx.open_opps if row["opportunity_type"] == "Expansion"]
    accounts = ctx.accounts
    target_accounts = {row["account_id"] for row in expansion}
    primary_contacts = [row for row in ctx.rows["crm-contacts.csv"] if row["account_id"] in target_accounts and row["is_primary"] == "true"]
    expected = sum_field(expansion, "expected_arr_usd")
    at_risk = [row for row in expansion if row["risk_status"] == "At risk"]
    earliest, latest = min(row["close_date"] for row in expansion), max(row["close_date"] for row in expansion)
    content = [so_what(f'Focus the expansion campaign on <strong>{fmt_int(len(target_accounts))} accounts</strong> with {fmt_int(len(expansion))} open Expansion opportunities. Those deals carry <strong>{money(expected)}</strong> of unweighted expected ARR. This is a proposed audience and plan, not a claim of campaign performance.')]
    content.append(kpis([
        ("Target accounts", fmt_int(len(target_accounts)), "Unique accounts with open Expansion deals"),
        ("Open Expansion deals", fmt_int(len(expansion)), money(expected) + " expected ARR"),
        ("Primary contacts", fmt_int(len(primary_contacts)), "One source contact per target account"),
        ("At-risk deals", fmt_int(len(at_risk)), money(sum_field(at_risk, "expected_arr_usd")) + " expected ARR"),
    ]))
    audience_rows = []
    for segment in sorted({accounts[row["account_id"]]["segment"] for row in expansion}):
        subset = [row for row in expansion if accounts[row["account_id"]]["segment"] == segment]
        audience_rows.append([segment, fmt_int(len({row["account_id"] for row in subset})), fmt_int(len(subset)), money(sum_field(subset, "expected_arr_usd")), fmt_int(sum(row["forecast_category"] == "Commit" for row in subset)), fmt_int(sum(row["risk_status"] == "At risk" for row in subset))])
    content.append(section(1, "Audience and exclusion rule", f'Include only accounts tied to an open opportunity whose type is Expansion in {ctx.forecast_period}. Exclude New Product and Renewal opportunities from this audience. Expected ARR remains unweighted and is not a revenue commitment.', table(["Segment", "Accounts", "Deals", "Expected ARR", "Commit deals", "At-risk deals"], audience_rows, numeric=[1, 2, 3, 4, 5], caption=f'{len(target_accounts)} unique target accounts; an account can have multiple Expansion deals')))
    product_items = []
    for product in sorted({row["product_family"] for row in expansion}):
        subset = [row for row in expansion if row["product_family"] == product]
        product_items.append((product, len(subset), f'{len(subset)} deals · {money(sum_field(subset, "expected_arr_usd"))}', TOKENS["secondary"]))
    content.append(section(2, "Message by product context", "Use the existing product family and account segment to frame an account review. Product mix is observed; the message and channel plan are proposals.", f'<div class="grid-2"><div class="card"><h3>Observed product mix</h3>{bar_list(product_items, "Open Expansion opportunities by product family")}</div><div class="card"><h3>Proposed message</h3><p>Review the open Expansion opportunity, the account plan and the next-step date with the primary contact. Use the source product family as the meeting context.</p><h3>Proposed call to action</h3><p>Confirm the next step and close-date plan with the opportunity owner. Do not imply a discount, product result or customer quote that is absent from the data.</p></div></div>'))
    owner_rows = []
    for owner in sorted({row["owner_alias"] for row in expansion}):
        subset = [row for row in expansion if row["owner_alias"] == owner]
        owner_rows.append([owner, fmt_int(len(subset)), money(sum_field(subset, "expected_arr_usd")), fmt_int(sum(row["forecast_category"] == "Commit" for row in subset)), fmt_int(sum(row["risk_status"] == "At risk" for row in subset)), min(row["close_date"] for row in subset)])
    content.append(section(3, "Owner execution plan", f'Close dates in the target set run from {earliest} to {latest}. Owner review should precede any contact attempt. At-risk deals need a next-step review rather than a broader message.', table(["Owner", "Deals", "Expected ARR", "Commit", "At risk", "Earliest close"], owner_rows, numeric=[1, 2, 3, 4])))
    measure_rows = [
        ["Audience coverage", fmt_int(len(primary_contacts)) + " primary contacts", "One primary contact joined for each unique target account", "Confirmed in synthetic source"],
        ["Owner review", fmt_int(len(expansion)) + " open deals", "Owner verifies stage, risk and next-step date", "Proposed gate"],
        ["Risk handling", fmt_int(len(at_risk)) + " at-risk deals", "Review before outreach; do not count as committed revenue", "Proposed gate"],
        ["Outcome capture", "Closed Won or Closed Lost", "Record outcome and reason in the opportunity source", "Proposed measurement"],
    ]
    content.append(section(4, "Gates and measurement", "Measure execution against source fields. No response rate, meetings booked or revenue lift is assumed in advance.", table(["Step", "Source denominator", "Rule", "Status"], measure_rows, classes="compact")))
    examples = sorted(expansion, key=lambda row: integer(row, "expected_arr_usd"), reverse=True)[:12]
    example_rows = [[accounts[row["account_id"]]["account_alias"], accounts[row["account_id"]]["segment"], row["product_family"], row["owner_alias"], forecast_badge(row["forecast_category"]), risk_badge(row["risk_status"]), row["close_date"], money(integer(row, "expected_arr_usd"))] for row in examples]
    content.append(section(5, "Representative target rows", "The 12 largest Expansion opportunities by expected ARR show the audience joins and fields used in this plan.", table(["Account", "Segment", "Product", "Owner", "Forecast", "Risk", "Close", "Expected ARR"], example_rows, numeric=[7], caption=f'12 rows from {len(expansion)} open Expansion opportunities') + f'<p class="small muted">Sources: {link("../data/crm-opportunities.csv", "opportunities")}, {link("../data/crm-contacts.csv", "contacts")} and {link("../data/crm-accounts.csv", "accounts")}.</p>'))
    return page(title="Expansion campaign one-pager", subtitle='A data-grounded audience, owner plan and measurement gates for existing open Expansion opportunities.', period=ctx.forecast_period, content="".join(content), generated_on=ctx.generated_on, sources=sources(ctx, ["crm-opportunities.csv", "crm-accounts.csv", "crm-contacts.csv"], depth=1), logo=ctx.logo, depth=1, validation_scope=f'{len(expansion)} open Expansion opportunities across {len(target_accounts)} unique synthetic accounts', validation_checks=["Campaign audience filters opportunity_type equals Expansion and open forecast is present", "Primary contact count is joined by account and is_primary", "Campaign actions are labeled proposed, not observed results"])


def build_win_loss(ctx: Context) -> str:
    closed = ctx.closed_opps
    won = [row for row in closed if row["stage"] == "Closed Won"]
    lost = [row for row in closed if row["stage"] == "Closed Lost"]
    p = ctx.manifest["pipeline"]
    content = [so_what(f'The closed set contains <strong>{fmt_int(len(won))} wins</strong> and <strong>{fmt_int(len(lost))} losses</strong>, a count-based win rate of <strong>{pct(len(won)/len(closed))}</strong>. Reason fields are complete within their applicable outcome. Competitor aliases are present only on losses, so win-side competitor comparisons are not supported.')]
    content.append(kpis([
        ("Closed deals", fmt_int(len(closed)), f"{ctx.arr_period} plus partial {ctx.forecast_period}"),
        ("Closed won", fmt_int(len(won)), money(sum_field(won, "expected_arr_usd")) + " expected ARR"),
        ("Closed lost", fmt_int(len(lost)), money(sum_field(lost, "expected_arr_usd")) + " expected ARR"),
        ("Count-based win rate", pct(len(won) / len(closed)), "Wins / all closed deals"),
    ]))
    period_rows = []
    for period in sorted({row["period"] for row in closed}):
        subset = [row for row in closed if row["period"] == period]
        w = [row for row in subset if row["stage"] == "Closed Won"]
        l = [row for row in subset if row["stage"] == "Closed Lost"]
        period_rows.append([period, fmt_int(len(w)), fmt_int(len(l)), pct(len(w) / len(subset)), money(sum_field(w, "expected_arr_usd")), money(sum_field(l, "expected_arr_usd")), max(row["close_date"] for row in subset)])
    content.append(section(1, "Outcome by period", f'{ctx.arr_period} is a full quarter. {ctx.forecast_period} closes extend only through the latest close date shown, so the periods are not a like-for-like trend comparison.', table(["Period", "Won", "Lost", "Win rate", "Won expected ARR", "Lost expected ARR", "Latest close"], period_rows, numeric=[1, 2, 3, 4, 5])))
    reason_rows = []
    for reason, count in Counter(row["win_reason"] for row in won).most_common():
        subset = [row for row in won if row["win_reason"] == reason]
        reason_rows.append(["Won", reason, fmt_int(count), pct(count / len(won)), money(sum_field(subset, "expected_arr_usd"))])
    for reason, count in Counter(row["loss_reason"] for row in lost).most_common():
        subset = [row for row in lost if row["loss_reason"] == reason]
        reason_rows.append(["Lost", reason, fmt_int(count), pct(count / len(lost)), money(sum_field(subset, "expected_arr_usd"))])
    content.append(section(2, "Recorded win and loss reasons", "Percentages use the applicable outcome as denominator. Reasons are recorded categories, not causal proof. Expected ARR on lost deals is the value that did not close won.", table(["Outcome", "Reason", "Deals", "Share of outcome", "Expected ARR"], reason_rows, numeric=[2, 3, 4])))
    coverage_rows = [
        ["Outcome", fmt_int(sum(row["stage"] in {"Closed Won", "Closed Lost"} for row in closed)), fmt_int(len(closed)), "Confirmed for every closed deal"],
        ["Win reason", fmt_int(sum(bool(row["win_reason"]) for row in won)), fmt_int(len(won)), "Applicable to Closed Won"],
        ["Loss reason", fmt_int(sum(bool(row["loss_reason"]) for row in lost)), fmt_int(len(lost)), "Applicable to Closed Lost"],
        ["Competitor alias on losses", fmt_int(sum(bool(row["competitor_alias"]) for row in lost)), fmt_int(len(lost)), "Alias presence does not mean Competitor was the loss reason"],
        ["Competitor alias on wins", fmt_int(sum(bool(row["competitor_alias"]) for row in won)), fmt_int(len(won)), "Not available; no win-side competitor comparison"],
    ]
    content.append(section(3, "Confirmed fields and limitations", "Field coverage is reported against the population where the field applies. Competitor aliases are anonymized labels, not verified company identities.", table(["Field", "Populated", "Applicable rows", "Interpretation"], coverage_rows, numeric=[1, 2], classes="compact") + '<div class="callout warn" style="margin-top:14px"><p>Do not infer why a deal closed from activity volume, competitor alias presence or stage history alone. No call transcripts, emails or buyer interviews are present.</p></div>'))
    competitor_rows = []
    for competitor in sorted({row["competitor_alias"] for row in lost}):
        subset = [row for row in lost if row["competitor_alias"] == competitor]
        competitor_rows.append([competitor, fmt_int(len(subset)), pct(len(subset) / len(lost)), fmt_int(sum(row["loss_reason"] == "Competitor" for row in subset)), money(sum_field(subset, "expected_arr_usd"))])
    content.append(section(4, "Competitor alias coverage on losses", "Every lost deal has an alias, while only the Competitor loss reason explicitly records competitive loss. The two fields answer different questions.", table(["Competitor alias", "Lost deals", "Share of losses", "Competitor loss reason", "Lost expected ARR"], competitor_rows, numeric=[1, 2, 3, 4])))
    examples = sorted(closed, key=lambda row: (row["close_date"], row["opportunity_alias"]), reverse=True)[:16]
    example_rows = [[row["opportunity_alias"], row["period"], row["stage"], row["owner_alias"], money(integer(row, "expected_arr_usd")), row["close_date"], row["win_reason"] or row["loss_reason"], row["competitor_alias"] or "Not provided"] for row in examples]
    content.append(section(5, "Representative closed rows", "The latest 16 closed deals by date and alias retain the fields used in this brief. Internal opportunity IDs are omitted.", table(["Deal", "Period", "Outcome", "Owner", "Expected ARR", "Close", "Reason", "Competitor"], example_rows, numeric=[4], caption=f'16 rows from {len(closed)} closed opportunities') + f'<p class="small muted">{link("../data/crm-opportunities.csv", "Open the full opportunity CSV")}.</p>'))
    return page(title="Win-loss brief", subtitle=f'Closed outcome, reason and competitor-field coverage across {ctx.arr_period} and partial {ctx.forecast_period}, with limitations made explicit.', period=f'{ctx.arr_period} and partial {ctx.forecast_period}', content="".join(content), generated_on=ctx.generated_on, sources=sources(ctx, ["crm-opportunities.csv"], depth=1), logo=ctx.logo, depth=1, validation_scope=f'All {len(closed)} synthetic closed opportunities: {len(won)} won and {len(lost)} lost', validation_checks=[f'Count-based win rate uses all {fmt_int(len(closed))} closed deals', "Reason coverage uses the applicable outcome denominator", f'Partial {ctx.forecast_period} is not presented as a like-for-like trend'])


def build_pipeline_analysis(ctx: Context) -> str:
    open_opps = sorted(ctx.open_opps, key=lambda row: (row["close_date"], row["opportunity_alias"]))
    accounts = ctx.accounts
    expected = sum_field(open_opps, "expected_arr_usd")
    at_risk = [row for row in open_opps if row["risk_status"] == "At risk"]
    content = [so_what(f'The open pipeline contains <strong>{fmt_int(len(open_opps))} deals</strong> and <strong>{money(expected)}</strong> of unweighted expected ARR. {fmt_int(len(at_risk))} deals are At risk, including {fmt_int(sum(row["forecast_category"] == "Commit" for row in at_risk))} in Commit. Filter and sort the complete row set below.')]
    content.append(kpis([
        ("Open deals", fmt_int(len(open_opps)), "All rows included below"),
        ("Expected ARR", money(expected), "Full pipeline, unweighted"),
        ("At-risk expected ARR", money(sum_field(at_risk, "expected_arr_usd")), f'{fmt_int(len(at_risk))} deals'),
        ("Commit expected ARR", money(ctx.manifest["pipeline"]["open_expected_arr_by_forecast"]["Commit"]), f'{ctx.manifest["pipeline"]["open_by_forecast"]["Commit"]} deals'),
    ]))
    stage_rows = []
    for stage in STAGE_ORDER:
        subset = [row for row in open_opps if row["stage"] == stage]
        stage_rows.append([stage, fmt_int(len(subset)), money(sum_field(subset, "expected_arr_usd")), pct(sum(integer(row, "probability") for row in subset) / len(subset) / 100), fmt_int(sum(row["risk_status"] == "At risk" for row in subset)), min(row["close_date"] for row in subset), max(row["close_date"] for row in subset)])
    content.append(section(1, "Stage detail", "Probability is a source field and is averaged for description only. Expected ARR and forecast views in this report are not probability weighted.", table(["Stage", "Deals", "Expected ARR", "Average probability", "At risk", "Earliest close", "Latest close"], stage_rows, numeric=[1, 2, 3, 4])))
    forecast_rows = []
    for category in FORECAST_ORDER:
        subset = [row for row in open_opps if row["forecast_category"] == category]
        forecast_rows.append([forecast_badge(category), fmt_int(len(subset)), money(sum_field(subset, "expected_arr_usd")), fmt_int(sum(row["risk_status"] == "At risk" for row in subset)), money(sum_field([row for row in subset if row["risk_status"] == "At risk"], "expected_arr_usd")), ", ".join(f'{stage}: {sum(row["stage"] == stage for row in subset)}' for stage in STAGE_ORDER)])
    content.append(section(2, "Forecast and risk detail", "Forecast categories are mutually exclusive. At-risk counts and expected ARR are overlays, not deductions from the category totals.", table(["Forecast", "Deals", "Expected ARR", "At-risk deals", "At-risk ARR", "Stage mix"], forecast_rows, numeric=[1, 2, 3, 4])))
    owner_rows = []
    for owner in sorted({row["owner_alias"] for row in open_opps}):
        subset = [row for row in open_opps if row["owner_alias"] == owner]
        owner_rows.append([owner, fmt_int(len(subset)), money(sum_field(subset, "expected_arr_usd")), money(sum(integer(row, "expected_arr_usd") for row in subset if row["forecast_category"] == "Commit")), fmt_int(sum(row["risk_status"] == "Watch" for row in subset)), fmt_int(sum(row["risk_status"] == "At risk" for row in subset)), min(row["next_step_date"] for row in subset)])
    content.append(section(3, "Owner and next-step coverage", "Every open deal has a next-step date. The earliest date shown per owner is a review cue, not evidence that the step is overdue.", table(["Owner", "Deals", "Expected ARR", "Commit ARR", "Watch", "At risk", "Earliest next step"], owner_rows, numeric=[1, 2, 3, 4, 5])))
    risk_rows = []
    for risk in RISK_ORDER:
        subset = [row for row in open_opps if row["risk_status"] == risk]
        risk_rows.append([risk_badge(risk), fmt_int(len(subset)), money(sum_field(subset, "expected_arr_usd")), fmt_int(sum(row["forecast_category"] == "Commit" for row in subset)), fmt_int(sum(row["forecast_category"] == "Best Case" for row in subset)), fmt_int(sum(row["forecast_category"] == "Pipeline" for row in subset))])
    content.append(section(4, "Risk by forecast category", "Risk status and forecast category are separate fields. Review at-risk Commit deals first when testing the commit view.", table(["Risk", "Deals", "Expected ARR", "Commit", "Best Case", "Pipeline"], risk_rows, numeric=[1, 2, 3, 4, 5], classes="compact")))
    options = lambda values: "".join(f'<option value="{esc(value)}">{esc(value)}</option>' for value in values)
    controls = f'''<div class="controls no-print">
<div class="control search"><label for="deal-search">Search deal, account or owner</label><input id="deal-search" type="search" autocomplete="off"></div>
<div class="control"><label for="stage-filter">Stage</label><select id="stage-filter"><option value="">All stages</option>{options(STAGE_ORDER)}</select></div>
<div class="control"><label for="forecast-filter">Forecast</label><select id="forecast-filter"><option value="">All forecasts</option>{options(FORECAST_ORDER)}</select></div>
<div class="control"><label for="risk-filter">Risk</label><select id="risk-filter"><option value="">All risk states</option>{options(RISK_ORDER)}</select></div>
<div class="control"><label for="owner-filter">Owner</label><select id="owner-filter"><option value="">All owners</option>{options(sorted({row["owner_alias"] for row in open_opps}))}</select></div>
<div class="control"><label for="deal-sort">Sort rows</label><select id="deal-sort"><option value="close">Close date</option><option value="value-desc">Expected ARR, high to low</option><option value="value-asc">Expected ARR, low to high</option><option value="owner">Owner and close date</option><option value="next">Next-step date</option></select></div>
</div><p class="result-count" id="deal-count" aria-live="polite">Showing {len(open_opps)} of {len(open_opps)} deals</p>'''
    detail_rows, row_attrs = [], []
    for row in open_opps:
        account = accounts[row["account_id"]]
        detail_rows.append([
            row["opportunity_alias"], account["account_alias"], row["owner_alias"], row["stage"], forecast_badge(row["forecast_category"]), risk_badge(row["risk_status"]), money(integer(row, "expected_arr_usd")), pct(integer(row, "probability") / 100, 0), row["close_date"], row["next_step_date"], row["product_family"], row["opportunity_type"],
        ])
        search = " ".join([row["opportunity_alias"], account["account_alias"], row["owner_alias"]]).lower()
        row_attrs.append(f'data-open-deal="true" data-stage="{esc(row["stage"])}" data-forecast="{esc(row["forecast_category"])}" data-risk="{esc(row["risk_status"])}" data-owner="{esc(row["owner_alias"])}" data-search="{esc(search)}" data-value="{integer(row, "expected_arr_usd")}" data-close="{row["close_date"]}" data-next="{row["next_step_date"]}"')
    full_table = table(["Deal", "Account", "Owner", "Stage", "Forecast", "Risk", "Expected ARR", "Probability", "Close", "Next step", "Product", "Type"], detail_rows, numeric=[6, 7], table_id="deal-table", row_attrs=row_attrs, caption=f'Complete {len(open_opps)}-deal open pipeline. Values are USD expected ARR.')
    open_csv_label = f"the {fmt_int(len(open_opps))}-row open-deal CSV"
    all_csv_label = f"all {fmt_int(len(ctx.rows['crm-opportunities.csv']))} opportunity rows"
    downloads = f'<p class="small muted">Download {link("../mock-pipeline.csv", open_csv_label)} or {link("../data/crm-opportunities.csv", all_csv_label)}. Filters run locally in this file.</p>'
    content.append(section(5, "Complete open-deal register", f'All {fmt_int(len(open_opps))} open deals are embedded, not a sample. Use any combination of filters. Clearing filters restores the full register.', controls + full_table + downloads))
    script = r"""
(function(){
  const table=document.getElementById('deal-table');
  const tbody=table.querySelector('tbody');
  const rows=Array.from(tbody.querySelectorAll('tr'));
  const count=document.getElementById('deal-count');
  const ids=['stage','forecast','risk','owner'];
  function apply(){
    const query=document.getElementById('deal-search').value.trim().toLowerCase();
    let visible=0;
    rows.forEach(function(row){
      let show=!query||row.dataset.search.includes(query);
      ids.forEach(function(id){const wanted=document.getElementById(id+'-filter').value;if(wanted&&row.dataset[id]!==wanted)show=false;});
      row.hidden=!show;if(show)visible++;
    });
    count.textContent='Showing '+visible+' of '+rows.length+' deals';
  }
  function sortRows(){
    const mode=document.getElementById('deal-sort').value;
    const sorted=rows.slice().sort(function(a,b){
      if(mode==='value-desc')return Number(b.dataset.value)-Number(a.dataset.value);
      if(mode==='value-asc')return Number(a.dataset.value)-Number(b.dataset.value);
      if(mode==='owner')return a.dataset.owner.localeCompare(b.dataset.owner)||a.dataset.close.localeCompare(b.dataset.close);
      if(mode==='next')return a.dataset.next.localeCompare(b.dataset.next)||a.dataset.close.localeCompare(b.dataset.close);
      return a.dataset.close.localeCompare(b.dataset.close)||a.dataset.search.localeCompare(b.dataset.search);
    });
    sorted.forEach(function(row){tbody.appendChild(row);});apply();
  }
  document.getElementById('deal-search').addEventListener('input',apply);
  ids.forEach(function(id){document.getElementById(id+'-filter').addEventListener('change',apply);});
  document.getElementById('deal-sort').addEventListener('change',sortRows);
  apply();
})();
"""
    return page(title="Open pipeline analysis", subtitle='Stage, forecast, owner and risk summaries backed by a filterable register of every open deal.', period=ctx.forecast_period, content="".join(content), generated_on=ctx.generated_on, sources=sources(ctx, ["crm-opportunities.csv", "crm-accounts.csv", "mock-pipeline.csv"], depth=1), logo=ctx.logo, depth=1, script=script, validation_scope=f'All {len(open_opps)} open synthetic opportunities, embedded as {len(detail_rows)} table rows', validation_checks=["Open register row count equals the manifest", "Stage, forecast, owner and risk aggregates reconcile to the register", "Full pipeline expected ARR is unweighted"])


def commission(credited: float, quota: dict[str, str]) -> tuple[float, float, float, float]:
    q = float(quota["quota_usd"])
    t1, t2 = float(quota["tier1_threshold"]), float(quota["tier2_threshold"])
    r1, r2, r3 = float(quota["tier1_rate"]), float(quota["tier2_rate"]), float(quota["tier3_rate"])
    first = min(max(credited, 0.0), q * t1) * r1
    second = min(max(credited - q * t1, 0.0), q * (t2 - t1)) * r2
    third = max(credited - q * t2, 0.0) * r3
    return first, second, third, first + second + third


def build_quota(ctx: Context) -> str:
    quotas = sorted(ctx.rows["quota-targets.csv"], key=lambda row: row["owner_alias"])
    q4_won = [row for row in ctx.closed_opps if row["period"] == ctx.forecast_period and row["stage"] == "Closed Won"]
    credited_total = sum_field(q4_won, "expected_arr_usd")
    quota_total = sum_field(quotas, "quota_usd")
    commissions = [commission(sum(integer(row, "expected_arr_usd") for row in q4_won if row["owner_id"] == quota["owner_id"]), quota)[3] for quota in quotas]
    content = [so_what(f'The {fmt_int(len(quotas))} owner quotas total <strong>{money(quota_total)}</strong> for {esc(ctx.forecast_period)}. Closed-won expected ARR credited in this illustration is <strong>{money(credited_total)}</strong>. Commission is calculated marginally by attainment band; open pipeline is not credited as earnings.')]
    content.append(kpis([
        ("Owners", fmt_int(len(quotas)), "One quota row per owner"),
        ("Total quota", money(quota_total), ctx.forecast_period + ", USD"),
        ("Closed-won credit", money(credited_total), pct(credited_total / quota_total) + " of total quota"),
        ("Illustrative commission", money(sum(commissions)), "Marginal tiers, before any policy adjustments"),
    ]))
    first = quotas[0]
    formula = f'<div class="card"><h3>Marginal formula</h3><p>For credit C and quota Q, using each owner\'s source thresholds and rates:</p><ul><li>Tier 1: rate 1 × min(C, Q × threshold 1).</li><li>Tier 2: rate 2 × min(max(C - Q × threshold 1, 0), Q × (threshold 2 - threshold 1)).</li><li>Tier 3: rate 3 × max(C - Q × threshold 2, 0).</li></ul><p><strong>Total commission = tier 1 + tier 2 + tier 3.</strong> Each band applies only to credit inside that band. Rates are not applied retroactively to all credit.</p><p class="small muted">Example source row: {esc(first["owner_alias"])} has quota {money(integer(first, "quota_usd"))}, thresholds {pct(float(first["tier1_threshold"]), 0)} and {pct(float(first["tier2_threshold"]), 0)}, and rates {pct(float(first["tier1_rate"]), 0)}, {pct(float(first["tier2_rate"]), 0)} and {pct(float(first["tier3_rate"]), 0)}.</p></div>'
    content.append(section(1, "Documented marginal tier logic", f'Credit means {ctx.forecast_period} Closed Won expected ARR in this synthetic example. Actual payroll policy, timing, refunds, clawbacks, caps and eligibility are not present in the data and are not modeled.', formula))
    owner_rows = []
    for quota in quotas:
        credited = sum(integer(row, "expected_arr_usd") for row in q4_won if row["owner_id"] == quota["owner_id"])
        t1, t2, t3, total = commission(credited, quota)
        owner_rows.append([quota["owner_alias"], money(integer(quota, "quota_usd")), money(credited), pct(credited / integer(quota, "quota_usd")), money(t1), money(t2), money(t3), money(total)])
    content.append(section(2, "Owner quota and commission illustration", f'Closed-won credit is joined by owner and limited to {ctx.forecast_period}. Zero credit produces zero commission. Attainment is credit divided by the owner\'s quota.', table(["Owner", "Quota", "Closed-won credit", "Attainment", "Tier 1", "Tier 2", "Tier 3", "Commission"], owner_rows, numeric=[1, 2, 3, 4, 5, 6, 7], caption=f'{ctx.forecast_period} marginal commission illustration, USD')))
    schedule_rows = []
    for quota in quotas:
        q = integer(quota, "quota_usd")
        schedule_rows.append([quota["owner_alias"], money(q), money(q * float(quota["tier1_threshold"])), pct(float(quota["tier1_rate"]), 0), money(q * (float(quota["tier2_threshold"]) - float(quota["tier1_threshold"]))), pct(float(quota["tier2_rate"]), 0), "Above " + money(q * float(quota["tier2_threshold"])), pct(float(quota["tier3_rate"]), 0)])
    content.append(section(3, "Band boundaries by owner", "Tier 1 width is quota × threshold 1. Tier 2 width is quota × (threshold 2 - threshold 1). Tier 3 applies only above quota × threshold 2.", table(["Owner", "Quota", "Tier 1 upper bound", "Rate 1", "Tier 2 band width", "Rate 2", "Tier 3 credit", "Rate 3"], schedule_rows, numeric=[1, 2, 3, 4, 5, 6, 7])))
    calculator_data = [{"owner": q["owner_alias"], "quota": integer(q, "quota_usd"), "t1": float(q["tier1_threshold"]), "t2": float(q["tier2_threshold"]), "r1": float(q["tier1_rate"]), "r2": float(q["tier2_rate"]), "r3": float(q["tier3_rate"]), "credit": sum(integer(row, "expected_arr_usd") for row in q4_won if row["owner_id"] == q["owner_id"])} for q in quotas]
    initial_t1, initial_t2, initial_t3, initial_total = commission(calculator_data[0]["credit"], quotas[0])
    initial_result = f'<strong>{esc(quotas[0]["owner_alias"])}: {money(initial_total)}</strong><br>Credit {money(calculator_data[0]["credit"])} · Attainment {pct(calculator_data[0]["credit"] / calculator_data[0]["quota"])}<br>Tier 1 {money(initial_t1)} · Tier 2 {money(initial_t2)} · Tier 3 {money(initial_t3)}'
    calculator = f'''<div class="card"><div class="controls"><div class="control"><label for="calc-owner">Owner</label><select id="calc-owner">{''.join(f'<option value="{i}">{esc(q["owner_alias"])}</option>' for i,q in enumerate(quotas))}</select></div><div class="control"><label for="calc-credit">Credited expected ARR, USD</label><input id="calc-credit" type="number" min="0" value="{calculator_data[0]["credit"]}"></div></div><div id="calc-result" class="callout" aria-live="polite">{initial_result}</div><p class="small muted" style="margin-top:12px;margin-bottom:0">This calculator applies only the source formula above. It does not create a payroll statement.</p></div>'''
    content.append(section(4, "Commission calculator", f'Choose an owner and enter any nonnegative credit amount to test the marginal bands. The default is that owner\'s {ctx.forecast_period} closed-won credit.', calculator))
    content.append(section(5, "Policy boundaries", "The source contains quota, thresholds and rates only. It does not contain payment dates, draws, recoveries, splits or manager overrides.", '<ul class="check-list"><li>All monetary aggregates use USD rows.</li><li>Open Commit, Best Case and Pipeline deals are excluded from credited commission.</li><li>Tier boundaries and rates come from quota-targets.csv, not from opportunity probabilities.</li><li>Visible people labels are synthetic owner aliases.</li></ul>'))
    script = "const quotaData=" + write_json_script(calculator_data) + ";\n" + r"""
(function(){
  const owner=document.getElementById('calc-owner');
  const credit=document.getElementById('calc-credit');
  const result=document.getElementById('calc-result');
  const fmt=function(value){return new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(value);};
  function calculate(){
    const q=quotaData[Number(owner.value)];
    const c=Math.max(0,Number(credit.value)||0);
    const first=Math.min(c,q.quota*q.t1)*q.r1;
    const second=Math.min(Math.max(c-q.quota*q.t1,0),q.quota*(q.t2-q.t1))*q.r2;
    const third=Math.max(c-q.quota*q.t2,0)*q.r3;
    const attainment=q.quota?c/q.quota*100:0;
    result.innerHTML='<strong>'+q.owner+': '+fmt(first+second+third)+'</strong><br>Credit '+fmt(c)+' · Attainment '+attainment.toFixed(1)+'%<br>Tier 1 '+fmt(first)+' · Tier 2 '+fmt(second)+' · Tier 3 '+fmt(third);
  }
  owner.addEventListener('change',function(){credit.value=quotaData[Number(owner.value)].credit;calculate();});
  credit.addEventListener('input',calculate);calculate();
})();
"""
    return page(title="Quota and commission", subtitle=f'Quota targets, closed-won credit and a fully documented marginal tier calculation for {fmt_int(len(quotas))} owners.', period=ctx.forecast_period, content="".join(content), generated_on=ctx.generated_on, sources=sources(ctx, ["quota-targets.csv", "crm-opportunities.csv"], depth=1), logo=ctx.logo, depth=1, script=script, validation_scope=f'All {len(quotas)} quota rows and {len(q4_won)} {ctx.forecast_period} closed-won opportunities', validation_checks=["Python and browser calculators use the same marginal formula", f'Only {ctx.forecast_period} Closed Won expected ARR is credited', "Open pipeline is excluded from commission"])


def build_project_plan(ctx: Context) -> str:
    generated = date.fromisoformat(ctx.generated_on)
    quotas = sorted(ctx.rows["quota-targets.csv"], key=lambda row: row["owner_alias"])
    owners = [row["owner_alias"] for row in quotas]
    arr_count = len(ctx.rows["arr-rollforward.csv"])
    opp_count = len(ctx.rows["crm-opportunities.csv"])
    history_count = len(ctx.rows["crm-stage-history.csv"])
    activity_count = len(ctx.rows["crm-activities.csv"])
    source_count = len(ctx.manifest["source_sha256"])
    open_count = len(ctx.open_opps)
    phases = [
        ("Source inventory", owners[0], 0, f'Catalog {source_count} hashed source files and assign field owners.', f'Every source file has a row count and SHA-256 hash.', "Evidence ready"),
        ("ARR reconciliation", owners[1], 7, f'Load and test {fmt_int(arr_count)} account-period rows.', 'Opening + new + expansion - contraction - churn = ending, with zero residual.', "Evidence ready"),
        ("CRM model checks", owners[2], 14, f'Join {fmt_int(opp_count)} opportunities, {fmt_int(history_count)} stage rows and {fmt_int(activity_count)} activities.', 'Primary keys are unique and foreign keys have no orphans.', "Evidence ready"),
        ("Forecast policy", owners[3], 21, f'Configure stage, risk and forecast reporting for {fmt_int(open_count)} open deals.', 'One exclusive forecast category per open deal; full pipeline remains unweighted.', "Evidence ready"),
        ("Report acceptance", owners[4], 28, 'Review ARR, forecast, pipeline and activation examples with revenue stakeholders.', 'Named reviewers approve metrics, limitations and row drill-downs.', "Proposed"),
        ("Release handoff", owners[5], 35, 'Package the approved examples, source dictionary and operating handoff.', 'Release owner accepts files and records the next review date.', "Proposed"),
    ]
    latest_end = generated + timedelta(days=39)
    content = [so_what(f'This proposed implementation plan uses the validated synthetic snapshot as acceptance evidence. The first four gates already have source evidence; stakeholder acceptance and release remain <strong>proposed</strong>. Dates run from {generated.isoformat()} to {latest_end.isoformat()} and are not commitments made by real people.')]
    content.append(kpis([
        ("Workstreams", fmt_int(len(phases)), "Sequential weekly gates"),
        ("Source files", fmt_int(source_count), "Hashed CSV inputs, including open extract"),
        ("Evidence-ready gates", fmt_int(sum(phase[5] == "Evidence ready" for phase in phases)), "Supported by manifest validation"),
        ("Proposed gates", fmt_int(sum(phase[5] == "Proposed" for phase in phases)), "No stakeholder sign-off claimed"),
    ]))
    plan_rows = []
    for name, owner, offset, work, gate, status in phases:
        start = generated + timedelta(days=offset)
        end = start + timedelta(days=4)
        plan_rows.append([name, owner, start.isoformat(), end.isoformat(), work, gate, badge(status, "good" if status == "Evidence ready" else "warn")])
    content.append(section(1, "Workstreams, owners and acceptance gates", "Owners are synthetic aliases from quota-targets.csv. Evidence ready means the source tests exist; it does not mean implementation work or organizational approval is complete.", table(["Workstream", "Owner", "Start", "End", "Scope", "Acceptance gate", "Status"], plan_rows, classes="compact")))
    total_days = 39
    timeline = [f'<div class="timeline" role="group" aria-label="Proposed {len(phases)}-workstream schedule over {total_days + 1} days">']
    for name, owner, offset, work, gate, status in phases:
        width = 5 / (total_days + 1) * 100
        left = offset / (total_days + 1) * 100
        start = generated + timedelta(days=offset)
        end = start + timedelta(days=4)
        timeline.append(f'<div class="timeline-row"><div><strong>{esc(name)}</strong><br><span class="small muted">{esc(owner)} · {start.isoformat()} to {end.isoformat()} · {esc(status)}</span></div><div class="timeline-track"><div class="timeline-bar" style="left:{left:.3f}%;width:{width:.3f}%" title="{esc(name)}">{esc(status)}</div></div></div>')
    timeline.append('</div>')
    content.append(section(2, "Proposed schedule", "Each workstream has a five-day schedule block and a gate before the next phase. The schedule is derived from the dataset generation date for this example.", f'<div class="card">{timeline}</div>'))
    gate_rows = [
        ["Source integrity", f'{source_count} files', f'{source_count} hashes match', "Passed in source manifest"],
        ["ARR", f'{arr_count:,} rows', "Zero residual at row and aggregate level", "Passed in source manifest"],
        ["CRM joins", f'{opp_count + history_count + activity_count:,} opportunity, history and activity rows', "No orphaned foreign keys", "Passed in source manifest"],
        ["Forecast", f'{open_count} open deals', "Exclusive categories and unweighted full pipeline", "Passed in source manifest and HTML build"],
        ["Report acceptance", "All required HTML examples", "Stakeholder review recorded", "Not claimed"],
        ["Release", "Approved handoff package", "Owner and next review recorded", "Not claimed"],
    ]
    content.append(section(3, "Gate register", "Passed gates refer only to automated source and build checks. Human approval gates remain explicitly unclaimed.", table(["Gate", "Population", "Acceptance test", "Current evidence"], gate_rows, classes="compact")))
    risk_rows = [
        ["Synthetic evidence only", "Metrics do not describe a live business.", "Label every artifact Synthetic / anonymized and retain source hashes.", owners[0]],
        [f"Partial {ctx.forecast_period} closed set", f"{ctx.forecast_period} win-loss is not comparable with a full {ctx.arr_period}.", "Show latest close date and prohibit trend claims without a matched period.", owners[1]],
        ["Competitor field coverage", "Competitor aliases are populated on losses only.", "Do not produce win-side competitor comparisons.", owners[2]],
        ["Activity interpretation", "CRM activity counts do not measure productivity.", "Keep activity summaries descriptive and pair them with opportunity evidence.", owners[3]],
    ]
    content.append(section(4, "Delivery risks and controls", "These controls follow from confirmed source limitations. They are implementation recommendations, not observed incidents.", table(["Risk", "Why it matters", "Control", "Owner"], risk_rows, classes="compact")))
    content.append(section(5, "Handoff package", "Review the generated HTML, source CSVs and data dictionary together. Office files are separate integration outputs and are not visually validated by this plan.", f'<p>{link("pipeline-analysis.html", "Pipeline analysis")} · {link("win-loss-brief.html", "Win-loss brief")} · {link("../index.html", "Master example gallery")} · {link("../data/data-dictionary.md", "Data dictionary")}</p>'))
    return page(title="Revenue reporting implementation plan", subtitle='A data-grounded rollout plan with synthetic owners, explicit evidence gates and unclaimed human approvals.', period=f'{generated.isoformat()} to {latest_end.isoformat()}', content="".join(content), generated_on=ctx.generated_on, sources=sources(ctx, ["manifest.json", "quota-targets.csv", "arr-rollforward.csv", "crm-opportunities.csv", "crm-stage-history.csv", "crm-activities.csv"], depth=1), logo=ctx.logo, depth=1, validation_scope=f'{source_count} hashed sources and six proposed implementation workstreams', validation_checks=["Schedule dates derive from manifest generation date", "Evidence-ready and proposed statuses are distinguished", "No human approval is claimed"])


def build_gallery(ctx: Context) -> str:
    m = ctx.manifest
    artifacts = [
        ("mock-arr-waterfall.html", "ARR waterfall", "Zero-baseline ARR bridge, segment detail and representative account movements."),
        ("mock-briefing-email.html", "Briefing email", "A leadership brief assembled from ARR, forecast, activation and activity rows."),
        ("mock-forecast.html", "Revenue forecast", "Exclusive forecast components, scenario arithmetic, stage mix and owner coverage."),
        ("mock-slides.html", "Browser slide companion", "Six keyboard-friendly slides covering ARR, forecast, activation and risk."),
        ("mock-activation-funnel.html", "Activation funnel", "Signup, activation and week-two retention by cohort and acquisition source."),
        ("mock-weekly-recap.html", "Weekly activity recap", "Matched seven-day windows, owner summaries and recent activity rows."),
        ("tour/mock-revenue-dashboard.html", "Revenue dashboard", "Combined ARR, forecast, stage and owner-risk readout."),
        ("tour/pipeline-motion.html", "Pipeline motion", "Animated stage-to-forecast mapping with pause, static and reduced-motion states."),
        ("tour/campaign-one-pager.html", "Expansion campaign", "Target accounts, product mix, owner execution and measurement gates."),
        ("tour/win-loss-brief.html", "Win-loss brief", "All closed deals with reason coverage and explicit competitor limitations."),
        ("tour/pipeline-analysis.html", "Pipeline analysis", "Stage, forecast, owner and risk summaries plus every open deal."),
        ("tour/quota-commission.html", "Quota and commission", "Source quotas, closed-won credit and a marginal tier calculator."),
        ("tour/project-plan.html", "Implementation plan", "Data-grounded workstreams, owners, schedule and acceptance gates."),
        ("index.html", "Master gallery", "This page: dataset inventory, validation evidence and every integration link."),
    ]
    content = [so_what(f'Review <strong>{fmt_int(len(artifacts))} self-contained HTML files</strong> built from {fmt_int(len(m["source_sha256"]))} hashed source files. Source validation passes and the HTML build reconciles headline metrics. Office links are provided for integration review without a visual-validation claim.')]
    content.append(kpis([
        ("ARR rows", fmt_int(m["tables"]["arr-rollforward.csv"]), f'{fmt_int(m["arr"]["ending_active_customers"])} ending active customers'),
        ("Opportunities", fmt_int(m["tables"]["crm-opportunities.csv"]), f'{fmt_int(m["pipeline"]["open_deals"])} open + {fmt_int(m["pipeline"]["closed_deals"])} closed'),
        ("Contacts and activities", fmt_int(m["tables"]["crm-contacts.csv"]), f'{fmt_int(m["tables"]["crm-activities.csv"])} activities'),
        ("Activation users", fmt_int(m["tables"]["activation-users.csv"]), f'{fmt_int(m["activation"]["activated"])} activated'),
    ]))
    cards = []
    for href, title, description in artifacts:
        label = "Open this gallery" if href == "index.html" else "Open example"
        cards.append(f'<article class="gallery-card"><span class="badge">HTML</span><h3>{esc(title)}</h3><p>{esc(description)}</p><a href="{esc(href)}">{label}<span class="sr-only">: {esc(title)}</span></a><code class="small muted">{esc(href)}</code></article>')
    content.append(section(1, "HTML example gallery", f'{len(artifacts)} HTML outputs are linked, including this gallery. The set uses inline CSS, JavaScript where needed, accessible SVG charts and an embedded Vera mark.', '<div class="gallery-grid">' + "".join(cards) + "</div>"))
    validation_labels = {
        "unique_primary_keys": "Unique primary keys",
        "zero_orphaned_foreign_keys": "Zero orphaned foreign keys",
        "arr_rows_reconcile": "ARR rows reconcile",
        "q3_crm_arr_reconciles": f"{ctx.arr_period} CRM and ARR reconcile",
        "anonymized_email_domain_only": "Anonymized email domain only",
    }
    validation_rows = [[label, badge("Passed", "good"), "Source manifest"] for key, label in validation_labels.items() for passed in [m["validation"][key]] if passed]
    validation_rows.extend([
        ["HTML required outputs", badge(f'{len(REQUIRED_OUTPUTS)} built', "good"), "Deterministic builder"],
        ["Headline metrics", badge("Recomputed", "good"), "ARR, forecast, activation, pipeline and activity checks"],
        ["Office visual rendering", badge("Not claimed", "warn"), "Separate integration review required"],
    ])
    content.append(section(2, "Validation status", "Passed labels refer to the fixed synthetic source snapshot and static HTML checks. They do not describe a live data connection or Office rendering.", table(["Check", "Status", "Evidence"], validation_rows, classes="compact")))
    dataset_rows = []
    for name in sorted(m["tables"]):
        dataset_rows.append([name, fmt_int(m["tables"][name]), link("data/" + name, "Open CSV"), m["source_sha256"][name][:12]])
    dataset_rows.append(["mock-pipeline.csv", fmt_int(len(ctx.rows["mock-pipeline.csv"])), link("mock-pipeline.csv", "Open CSV"), m["source_sha256"]["mock-pipeline.csv"][:12]])
    dataset_rows.append(["manifest.json", "Canonical metrics", link("data/manifest.json", "Open manifest"), hashlib.sha256(MANIFEST_PATH.read_bytes()).hexdigest()[:12]])
    content.append(section(3, "Source files and hashes", f'The manifest records {fmt_int(m["total_linked_records"])} total linked records across its table inventory. Hash prefixes are the first 12 characters of SHA-256.', table(["Source", "Rows or role", "Link", "SHA-256 prefix"], dataset_rows, numeric=[1]) + f'<p>{link("data/data-dictionary.md", "Open the data dictionary")} <span class="small muted">(integration path, once present)</span></p>'))
    office = [
        ("mock-arr-rollforward.xlsx", "ARR roll-forward workbook"),
        ("documents/mock-revenue-review.docx", "Revenue review document"),
        ("documents/mock-pipeline-review.docx", "Pipeline review document"),
        ("documents/mock-campaign-one-pager.docx", "Campaign one-pager document"),
        ("documents/mock-project-plan.docx", "Project plan document"),
        ("presentations/mock-revenue-review.pptx", "Revenue review presentation"),
    ]
    office_cards = [f'<article class="gallery-card"><span class="badge secondary">Office</span><h3>{esc(title)}</h3><p>Companion integration path. Visual rendering is not asserted by the HTML build.</p>{link(href, "Open companion path")}<code class="small muted">{esc(href)}</code></article>' for href, title in office]
    content.append(section(4, "Office companion paths", "These links are included for the combined example set. Presence and rendering of Office files must be reviewed separately.", '<div class="gallery-grid">' + "".join(office_cards) + "</div>"))
    definitions = [
        ["ARR", "Annual recurring revenue in USD. The roll-forward is account-level."],
        ["NRR", "(Starting ARR + expansion - contraction - churn) / starting ARR. New ARR is excluded."],
        ["GRR", "(Starting ARR - contraction - churn) / starting ARR."],
        ["Expected ARR", "The opportunity expected_arr_usd field. Full pipeline is the unweighted sum."],
        ["Commit view", f"{ctx.forecast_period} closed-won expected ARR plus open Commit expected ARR."],
        ["Activation", "The activated user flag. Week-two retention is a separate retained_w2 flag."],
        ["Win rate", "Closed Won deals / all closed deals by count, unless another denominator is named."],
    ]
    content.append(section(5, "Metric definitions", "Definitions are repeated here so gallery reviewers can reconcile examples without assuming a hidden model.", table(["Term", "Definition"], definitions, classes="compact")))
    return page(title="Vera rich example gallery", subtitle='A complete, traceable set of synthetic RevOps HTML examples with source and Office integration links.', period=f'{ctx.arr_period} and {ctx.forecast_period}', content="".join(content), generated_on=ctx.generated_on, sources=sources(ctx, ["manifest.json"]), logo=ctx.logo, hero_badges=[f'{len(artifacts)} HTML files', "Source checks passed"], validation_scope=f'All manifest source tables, {len(artifacts)} HTML outputs and six Office integration paths', validation_checks=["Gallery links every required HTML output", "Dataset counts and validation states come from the manifest", "Office visual validation is explicitly not claimed"])


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[tuple[str, str]] = []
        self.svg_count = 0
        self.svg_titles = 0
        self.svg_descs = 0
        self.skip_text = 0
        self.visible_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.skip_text += 1
        values = dict(attrs)
        if tag == "svg":
            self.svg_count += 1
        if tag == "title" and self.svg_count > self.svg_titles:
            self.svg_titles += 1
        if tag == "desc" and self.svg_count > self.svg_descs:
            self.svg_descs += 1
        for attr in ("href", "src"):
            if values.get(attr):
                self.references.append((attr, str(values[attr])))

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip_text:
            self.skip_text -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip_text:
            self.visible_text.append(data)


def luminance(hex_color: str) -> float:
    channels = [int(hex_color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(first: str, second: str) -> float:
    l1, l2 = sorted([luminance(first), luminance(second)], reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def run_static_checks(ctx: Context, outputs: dict[str, str]) -> dict[str, object]:
    errors: list[str] = []
    pending: list[str] = []
    reference_count = 0
    unfinished = re.compile(r"\b(?:TBD|TODO|FIXME|lorem ipsum|mock artifact|full interactive version|fake data|coming soon|placeholder)\b", re.I)
    banned = re.compile(r"\b(?:unleash|elevate|seamless|next-gen|transformative|revolutionize|robust|cutting-edge|leverage|powerful solution)\b", re.I)
    for relative in REQUIRED_OUTPUTS:
        path = BASE / relative
        if not path.is_file():
            errors.append(f"Missing required output: {relative}")
            continue
        text = outputs[relative]
        if path.read_text(encoding="utf-8") != text:
            errors.append(f"Written output differs from builder content: {relative}")
        for required_text in ["Synthetic / anonymized", f'Built by Vera {ctx.generated_on}', "Validated by Vera", 'name="viewport"']:
            if required_text not in text:
                errors.append(f"Missing required stamp or viewport in {relative}: {required_text}")
        if "—" in text:
            errors.append(f"Em dash found: {relative}")
        match = unfinished.search(text)
        if match:
            errors.append(f"Unfinished marker {match.group(0)!r} in {relative}")
        match = banned.search(text)
        if match:
            errors.append(f"Banned phrase {match.group(0)!r} in {relative}")
        if re.search(r"(?:src|href)=[\"'](?:https?:)?//", text, re.I) or re.search(r"@import|url\(\s*[\"']?(?:https?:)?//", text, re.I):
            errors.append(f"External asset reference in {relative}")
        for responsive_marker in ["@media (max-width: 390px)", "prefers-reduced-motion", ".table-wrap { max-width: 100%; overflow: auto;", ".chart-scroll { max-width: 100%; overflow-x: auto;"]:
            if responsive_marker not in text:
                errors.append(f"Responsive safeguard missing in {relative}: {responsive_marker}")
        parser = AssetParser()
        parser.feed(text)
        visible_text = " ".join(parser.visible_text)
        if re.search(r"\b(?:opp|acct|owner|user|act|hist|contact)_\d+\b", visible_text):
            errors.append(f"Unresolved internal ID visible in {relative}")
        if parser.svg_count != parser.svg_titles or parser.svg_count != parser.svg_descs:
            errors.append(f"SVG title/description mismatch in {relative}: {parser.svg_count} graphics, {parser.svg_titles} titles, {parser.svg_descs} descriptions")
        for attr, reference in parser.references:
            reference_count += 1
            if reference.startswith(("data:", "#")):
                continue
            parsed = urlsplit(reference)
            if parsed.scheme or parsed.netloc:
                errors.append(f"External or unsupported URL in {relative}: {reference}")
                continue
            target = (path.parent / unquote(parsed.path)).resolve()
            try:
                target_relative = target.relative_to(BASE.resolve()).as_posix()
            except ValueError:
                errors.append(f"Link escapes examples tree in {relative}: {reference}")
                continue
            if not target.exists():
                if target_relative in FUTURE_LINKS or target_relative == "mock-arr-rollforward.xlsx":
                    pending.append(f"{relative} -> {target_relative}")
                else:
                    errors.append(f"Missing linked file in {relative}: {reference}")
    week = weekly_activity(ctx)
    current_activities = week["current"]
    expansion = [row for row in ctx.open_opps if row["opportunity_type"] == "Expansion"]
    expansion_accounts = {row["account_id"] for row in expansion}
    quotas = ctx.rows["quota-targets.csv"]
    q4_won_rows = [row for row in ctx.closed_opps if row["period"] == ctx.forecast_period and row["stage"] == "Closed Won"]
    headline_requirements = {
        "index.html": [fmt_int(ctx.manifest["tables"]["arr-rollforward.csv"]), fmt_int(ctx.manifest["pipeline"]["open_deals"]), fmt_int(ctx.manifest["total_linked_records"])],
        "mock-arr-waterfall.html": [money(ctx.manifest["arr"]["starting_arr"]), money(ctx.manifest["arr"]["ending_arr"]), pct(ctx.manifest["arr"]["nrr"])],
        "mock-forecast.html": [money(ctx.manifest["pipeline"]["commit_view"]), money(ctx.manifest["pipeline"]["best_case_view"]), money(ctx.manifest["pipeline"]["full_pipeline_view"])],
        "mock-activation-funnel.html": [fmt_int(ctx.manifest["activation"]["signups"]), fmt_int(ctx.manifest["activation"]["activated"]), pct(ctx.manifest["activation"]["activation_rate"])],
        "mock-briefing-email.html": [money(ctx.manifest["arr"]["ending_arr"]), money(ctx.manifest["pipeline"]["commit_view"])],
        "mock-slides.html": [money(ctx.manifest["arr"]["ending_arr"]), money(ctx.manifest["pipeline"]["commit_view"])],
        "mock-weekly-recap.html": [fmt_int(len(current_activities)), f'{week["start"].isoformat()} to {week["end"].isoformat()}', pct((len(current_activities) - len(week["prior"])) / len(week["prior"]))],
        "tour/mock-revenue-dashboard.html": [money(ctx.manifest["arr"]["ending_arr"]), money(ctx.manifest["pipeline"]["commit_view"])],
        "tour/pipeline-motion.html": [fmt_int(len(ctx.open_opps)), money(sum_field(ctx.open_opps, "expected_arr_usd"))],
        "tour/campaign-one-pager.html": [fmt_int(len(expansion)), fmt_int(len(expansion_accounts)), money(sum_field(expansion, "expected_arr_usd"))],
        "tour/pipeline-analysis.html": [money(ctx.manifest["pipeline"]["open_expected_arr_total"]), fmt_int(ctx.manifest["pipeline"]["open_deals"])],
        "tour/quota-commission.html": [money(sum_field(quotas, "quota_usd")), money(sum_field(q4_won_rows, "expected_arr_usd"))],
        "tour/project-plan.html": [fmt_int(len(ctx.rows["arr-rollforward.csv"])), fmt_int(len(ctx.open_opps)), ctx.generated_on],
        "tour/win-loss-brief.html": [fmt_int(ctx.manifest["pipeline"]["closed_won"]), fmt_int(ctx.manifest["pipeline"]["closed_lost"]), pct(ctx.manifest["pipeline"]["closed_win_rate"])],
    }
    for relative, values in headline_requirements.items():
        for value in values:
            if value not in outputs[relative]:
                errors.append(f"Headline metric {value} missing or mismatched in {relative}")
    pipeline_rows = outputs["tour/pipeline-analysis.html"].count('data-open-deal="true"')
    if pipeline_rows != len(ctx.open_opps):
        errors.append(f"Open pipeline register has {pipeline_rows} rows, expected {len(ctx.open_opps)}")
    color_pairs = [
        (TOKENS["ink"], TOKENS["surface"]), (TOKENS["muted"], TOKENS["surface"]),
        (TOKENS["muted"], TOKENS["paper"]), (TOKENS["surface"], TOKENS["accent"]),
        (TOKENS["surface"], TOKENS["dark"]), (TOKENS["accent_ink"], TOKENS["accent_soft"]),
        (TOKENS["secondary_ink"], TOKENS["secondary_soft"]), (TOKENS["good_ink"], TOKENS["good_soft"]),
        (TOKENS["warn_ink"], TOKENS["warn_soft"]), (TOKENS["risk_ink"], TOKENS["risk_soft"]),
        (TOKENS["surface"], TOKENS["secondary_ink"]), (TOKENS["surface"], TOKENS["good_ink"]),
        (TOKENS["dark_muted"], TOKENS["dark"]), (TOKENS["surface"], TOKENS["dark_line"]),
        (TOKENS["good_ink"], TOKENS["paper"]), (TOKENS["accent_ink"], TOKENS["paper"]),
    ]
    contrast_results = {f"{first} on {second}": round(contrast(first, second), 2) for first, second in color_pairs}
    for pair, ratio in contrast_results.items():
        if ratio < 4.5:
            errors.append(f"Body-text contrast below 4.5: {pair} = {ratio}")
    return {
        "status": "PASS" if not errors else "FAIL",
        "required_html_files": len(REQUIRED_OUTPUTS),
        "html_bytes": sum(len(outputs[name].encode("utf-8")) for name in REQUIRED_OUTPUTS),
        "references_checked": reference_count,
        "headline_files_checked": len(headline_requirements),
        "pipeline_rows_checked": pipeline_rows,
        "contrast_ratios": contrast_results,
        "pending_integration_links": sorted(set(pending)),
        "errors": errors,
    }


def main() -> None:
    ctx = load_context()
    builders = {
        "mock-arr-waterfall.html": build_arr,
        "mock-briefing-email.html": build_briefing,
        "mock-forecast.html": build_forecast,
        "mock-slides.html": build_slides,
        "mock-activation-funnel.html": build_activation,
        "mock-weekly-recap.html": build_weekly,
        "tour/mock-revenue-dashboard.html": build_dashboard,
        "tour/pipeline-motion.html": build_pipeline_motion,
        "tour/campaign-one-pager.html": build_campaign,
        "tour/win-loss-brief.html": build_win_loss,
        "tour/pipeline-analysis.html": build_pipeline_analysis,
        "tour/quota-commission.html": build_quota,
        "tour/project-plan.html": build_project_plan,
        "index.html": build_gallery,
    }
    outputs: dict[str, str] = {}
    for relative in REQUIRED_OUTPUTS:
        outputs[relative] = builders[relative](ctx)
        destination = BASE / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(outputs[relative], encoding="utf-8")
    result = run_static_checks(ctx, outputs)
    print(json.dumps({"build": result, "files": REQUIRED_OUTPUTS}, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
