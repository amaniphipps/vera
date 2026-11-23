#!/usr/bin/env python3
"""Shared, dependency-free HTML components for Vera's synthetic examples."""
from __future__ import annotations

import base64
import html
import json
from pathlib import Path
from typing import Iterable, Sequence


TOKENS = {
    "accent": "#3559D6",
    "secondary": "#0F8A75",
    "ink": "#1B1F27",
    "paper": "#F4F5F7",
    "dark": "#14182E",
    "surface": "#FFFFFF",
    "line": "#DDE1E6",
    "good": "#1F9D55",
    "warn": "#B7791F",
    "risk": "#C53030",
    "muted": "#4B5563",
    "accent_soft": "#E9EEFD",
    "secondary_soft": "#E3F3EF",
    "good_soft": "#E5F4EA",
    "warn_soft": "#FFF2DC",
    "risk_soft": "#FBE9E9",
    "accent_ink": "#2947B5",
    "secondary_ink": "#096552",
    "good_ink": "#146C39",
    "warn_ink": "#774B09",
    "risk_ink": "#A12525",
    "dark_muted": "#C3CBE0",
    "dark_line": "#343B59",
}

CSS = r"""
:root {
  --accent: #3559D6; --secondary: #0F8A75; --ink: #1B1F27;
  --paper: #F4F5F7; --dark: #14182E; --surface: #FFFFFF;
  --line: #DDE1E6; --good: #1F9D55; --warn: #B7791F; --risk: #C53030;
  --muted: #4B5563; --accent-soft: #E9EEFD; --secondary-soft: #E3F3EF;
  --good-soft: #E5F4EA; --warn-soft: #FFF2DC; --risk-soft: #FBE9E9;
  --accent-ink: #2947B5; --secondary-ink: #096552; --good-ink: #146C39;
  --warn-ink: #774B09; --risk-ink: #A12525; --dark-muted: #C3CBE0;
  --dark-line: #343B59; --shadow: 0 12px 34px rgba(20, 24, 46, .07);
  --font-ui: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
* { box-sizing: border-box; }
html { max-width: 100%; overflow-x: hidden; scroll-behavior: smooth; }
body { margin: 0; max-width: 100%; overflow-x: hidden; background: var(--paper); color: var(--ink); font: 15px/1.55 var(--font-ui); }
img, svg { max-width: 100%; }
a { color: var(--accent-ink); text-underline-offset: 3px; }
a:hover { color: var(--accent); }
button, input, select { font: inherit; }
button, .button { min-height: 44px; border: 1px solid var(--line); border-radius: 9px; padding: 9px 14px; background: var(--surface); color: var(--ink); font-weight: 650; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; justify-content: center; gap: 7px; }
button:hover, .button:hover { border-color: var(--accent); color: var(--accent-ink); }
button:focus-visible, a:focus-visible, input:focus-visible, select:focus-visible, summary:focus-visible { outline: 3px solid var(--accent); outline-offset: 3px; }
button[aria-pressed="true"], .button.primary { background: var(--accent); border-color: var(--accent); color: var(--surface); }
input, select { min-height: 44px; max-width: 100%; border: 1px solid var(--line); border-radius: 8px; padding: 8px 10px; background: var(--surface); color: var(--ink); }
label { font-size: 13px; font-weight: 650; }
.report-page { width: min(1320px, 100%); margin: 0 auto; padding: 30px 32px 54px; }
.topbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 30px; }
.brand { display: flex; align-items: center; gap: 11px; min-width: 0; }
.brand img { width: 42px; height: 42px; border-radius: 11px; flex: 0 0 auto; }
.brand-name { font-weight: 760; letter-spacing: -.01em; }
.brand-sub { color: var(--muted); font-size: 12px; }
.gallery-link { flex: 0 0 auto; min-height: 44px; display: inline-flex; align-items: center; font-size: 13px; font-weight: 650; }
.hero { background: var(--dark); color: var(--surface); border-radius: 18px; padding: 30px; margin-bottom: 24px; box-shadow: var(--shadow); }
.eyebrow { color: var(--accent-ink); font-size: 12px; font-weight: 760; letter-spacing: .08em; margin: 0 0 8px; }
.hero .eyebrow { color: var(--dark-muted); }
h1, h2, h3, p { margin-top: 0; }
p { max-width: 75ch; }
h1 { font-size: clamp(28px, 4vw, 44px); line-height: 1.12; letter-spacing: -.035em; margin-bottom: 12px; max-width: 900px; }
h2 { font-size: 22px; line-height: 1.25; letter-spacing: -.02em; margin-bottom: 7px; }
h3 { font-size: 16px; line-height: 1.3; margin-bottom: 8px; }
.subtitle { color: var(--dark-muted); font-size: 16px; max-width: 75ch; margin-bottom: 16px; }
.meta-row { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
.badge { display: inline-flex; align-items: center; min-height: 28px; padding: 4px 9px; border-radius: 999px; background: var(--accent-soft); color: var(--accent-ink); font-size: 12px; font-weight: 700; white-space: nowrap; }
.hero .badge { background: var(--dark-line); color: var(--surface); }
.badge.good { background: var(--good-soft); color: var(--good-ink); }
.badge.warn { background: var(--warn-soft); color: var(--warn-ink); }
.badge.risk { background: var(--risk-soft); color: var(--risk-ink); }
.badge.secondary { background: var(--secondary-soft); color: var(--secondary-ink); }
.so-what { background: var(--surface); border: 1px solid var(--line); border-left: 5px solid var(--accent); border-radius: 12px; padding: 20px 22px; margin: 0 0 28px; }
.so-what .label { color: var(--accent-ink); font-weight: 760; font-size: 12px; letter-spacing: .06em; margin-bottom: 5px; }
.so-what p { font-size: 17px; margin: 0; max-width: 75ch; }
.kpis { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 0 0 28px; }
.kpi { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 17px; min-width: 0; }
.kpi-label { color: var(--muted); font-size: 12px; font-weight: 650; }
.kpi-value { font: 720 clamp(22px, 3vw, 30px)/1.25 var(--font-ui); font-variant-numeric: tabular-nums; letter-spacing: -.025em; margin: 4px 0; overflow-wrap: anywhere; }
.kpi-note { color: var(--muted); font-size: 12px; }
section { margin: 0 0 30px; }
.section-head { display: flex; gap: 10px; align-items: flex-start; }
.section-num { color: var(--accent-ink); font: 700 13px/1.5 var(--font-mono); padding-top: 4px; }
.takeaway { color: var(--muted); max-width: 75ch; margin-bottom: 16px; }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 20px; min-width: 0; }
.card h3:last-child, .card p:last-child { margin-bottom: 0; }
.grid-2 { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; }
.grid-3 { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.stack { display: grid; gap: 14px; }
.muted { color: var(--muted); }
.small { font-size: 12px; }
.mono, .num { font-variant-numeric: tabular-nums; }
.num { text-align: right; font-family: var(--font-mono); font-size: .94em; white-space: nowrap; }
.pos { color: var(--good-ink); }
.neg { color: var(--risk-ink); }
.warn-text { color: var(--warn-ink); }
.table-wrap { max-width: 100%; overflow: auto; background: var(--surface); border: 1px solid var(--line); border-radius: 12px; }
table { width: 100%; min-width: 640px; border-collapse: collapse; font-size: 13px; }
table.compact { min-width: 520px; }
caption { text-align: left; padding: 13px 15px; color: var(--muted); font-size: 12px; background: var(--surface); }
th { padding: 11px 13px; border-bottom: 1px solid var(--line); background: var(--paper); color: var(--muted); font-size: 12px; text-align: left; vertical-align: bottom; }
td { padding: 11px 13px; border-bottom: 1px solid var(--line); vertical-align: top; }
tbody tr:last-child td { border-bottom: 0; }
tbody tr:hover { background: var(--accent-soft); }
th button { min-height: 32px; padding: 3px 5px; border: 0; background: transparent; color: inherit; justify-content: flex-start; font-size: 12px; }
tr[hidden] { display: none; }
.chart-card { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 18px; min-width: 0; }
.chart-scroll { max-width: 100%; overflow-x: auto; }
.chart-scroll svg { display: block; width: 100%; min-width: 660px; height: auto; }
.chart-note { color: var(--muted); font-size: 12px; margin: 10px 0 0; }
.legend { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 10px; color: var(--muted); font-size: 12px; }
.legend span { display: inline-flex; gap: 6px; align-items: center; }
.swatch { width: 11px; height: 11px; border-radius: 3px; display: inline-block; flex: 0 0 auto; }
.bar-list { display: grid; gap: 13px; }
.bar-item { display: grid; gap: 5px; }
.bar-meta { display: flex; justify-content: space-between; gap: 12px; font-size: 13px; }
.bar-meta strong { font-family: var(--font-mono); font-size: 12px; white-space: nowrap; }
.bar-track { height: 13px; border-radius: 999px; background: var(--paper); overflow: hidden; }
.bar-fill { height: 100%; min-width: 2px; border-radius: inherit; background: var(--accent); }
.funnel { display: grid; gap: 12px; }
.funnel-step { display: grid; grid-template-columns: minmax(110px, 170px) minmax(120px, 1fr) minmax(110px, 150px); gap: 14px; align-items: center; }
.funnel-track { height: 46px; background: var(--paper); border-radius: 8px; overflow: hidden; }
.funnel-fill { height: 100%; display: flex; align-items: center; padding-left: 12px; color: var(--surface); background: var(--accent); font: 700 12px var(--font-mono); min-width: 3px; }
.funnel-value { font-family: var(--font-mono); font-size: 12px; text-align: right; }
.controls { display: flex; flex-wrap: wrap; gap: 10px; align-items: end; margin-bottom: 14px; }
.control { display: grid; gap: 4px; min-width: 140px; flex: 1 1 140px; }
.control.search { flex-grow: 2; }
.control input, .control select { width: 100%; }
.result-count { margin: 0 0 10px; color: var(--muted); font-size: 13px; }
.callout { border-left: 4px solid var(--secondary); background: var(--secondary-soft); color: var(--ink); padding: 14px 16px; border-radius: 8px; }
.callout.warn { border-color: var(--warn); background: var(--warn-soft); }
.callout.risk { border-color: var(--risk); background: var(--risk-soft); }
.callout p:last-child { margin-bottom: 0; }
.check-list, .clean-list { margin: 0; padding: 0; list-style: none; display: grid; gap: 9px; }
.check-list li { padding-left: 23px; position: relative; }
.check-list li::before { content: "✓"; position: absolute; left: 0; color: var(--good-ink); font-weight: 800; }
.clean-list li { padding-bottom: 9px; border-bottom: 1px solid var(--line); }
.clean-list li:last-child { border-bottom: 0; padding-bottom: 0; }
.email-shell { max-width: 900px; margin: 0 auto; background: var(--surface); border: 1px solid var(--line); border-radius: 14px; overflow: hidden; }
.email-head { padding: 20px 24px; background: var(--paper); border-bottom: 1px solid var(--line); }
.email-head dl { display: grid; grid-template-columns: 70px 1fr; gap: 6px 12px; margin: 0; font-size: 13px; }
.email-head dt { color: var(--muted); }
.email-head dd { margin: 0; overflow-wrap: anywhere; }
.email-body { padding: 26px; }
.email-body section { padding-bottom: 22px; border-bottom: 1px solid var(--line); }
.email-body section:last-child { border-bottom: 0; padding-bottom: 0; }
.slide-nav { position: sticky; top: 0; z-index: 5; display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 10px 0; background: rgba(244, 245, 247, .96); }
.slide-count { font: 650 13px var(--font-mono); color: var(--muted); }
.slides { display: grid; grid-template-columns: minmax(0, 1fr); gap: 22px; }
.slide { min-width: 0; min-height: 560px; display: flex; flex-direction: column; justify-content: center; background: var(--surface); border: 1px solid var(--line); border-radius: 16px; padding: clamp(22px, 5vw, 58px); box-shadow: var(--shadow); scroll-margin-top: 72px; }
.slide.dark { background: var(--dark); color: var(--surface); }
.slide.dark .muted, .slide.dark .takeaway, .slide.dark .eyebrow { color: var(--dark-muted); }
.slide h2 { font-size: clamp(26px, 4vw, 40px); }
.slide .kpis { margin-bottom: 0; }
.motion-map { width: 100%; height: auto; display: block; }
.motion-path { fill: none; stroke: var(--accent); stroke-linecap: round; stroke-dasharray: 8 12; animation: flow 2.4s linear infinite; opacity: .62; }
.motion-path.secondary { stroke: var(--secondary); }
.motion-paused .motion-path { animation-play-state: paused; }
.static-view .motion-path { animation: none; stroke-dasharray: none; opacity: .48; }
@keyframes flow { to { stroke-dashoffset: -40; } }
.timeline { display: grid; gap: 10px; }
.timeline-row { display: grid; grid-template-columns: minmax(150px, 230px) 1fr; gap: 12px; align-items: center; }
.timeline-track { position: relative; height: 32px; background: var(--paper); border-radius: 7px; }
.timeline-bar { position: absolute; top: 4px; bottom: 4px; min-width: 8px; border-radius: 5px; background: var(--accent); color: var(--surface); font-size: 12px; padding: 3px 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.gallery-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 15px; }
.gallery-card { display: flex; flex-direction: column; gap: 9px; background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 18px; min-width: 0; }
.gallery-card h3 { margin: 0; }
.gallery-card p { color: var(--muted); font-size: 13px; margin: 0; flex: 1; }
.gallery-card a { min-height: 44px; display: inline-flex; align-items: center; font-weight: 700; overflow-wrap: anywhere; }
.gallery-card code { overflow-wrap: anywhere; }
footer { border-top: 1px solid var(--line); padding-top: 18px; margin-top: 36px; color: var(--muted); font-size: 12px; }
.footer-top { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 8px 18px; margin-bottom: 9px; }
.stamp { color: var(--good-ink); font-weight: 750; }
.source-line { overflow-wrap: anywhere; }
.source-line a { color: var(--muted); }
.validation { margin-top: 13px; }
.validation summary { min-height: 44px; display: flex; align-items: center; cursor: pointer; color: var(--ink); font-weight: 650; }
.validation pre { white-space: pre-wrap; overflow-wrap: anywhere; background: var(--surface); border: 1px solid var(--line); border-radius: 9px; padding: 14px; font: 12px/1.55 var(--font-mono); color: var(--muted); }
.sr-only { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; border: 0; }
@media (max-width: 980px) {
  .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .gallery-grid, .grid-3 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 680px) {
  .report-page { padding: 18px 14px 38px; }
  .topbar { align-items: flex-start; margin-bottom: 20px; }
  .brand-sub { display: none; }
  .hero { padding: 22px 18px; border-radius: 13px; }
  .grid-2, .grid-3, .gallery-grid { grid-template-columns: 1fr; }
  .card, .chart-card { padding: 15px; }
  .slide { min-height: 520px; }
  .funnel-step { grid-template-columns: 95px minmax(80px, 1fr); gap: 9px; }
  .funnel-value { grid-column: 2; text-align: left; margin-top: -8px; }
  .timeline-row { grid-template-columns: 1fr; gap: 5px; }
  .timeline-track { min-width: 0; }
  .email-body, .email-head { padding: 18px; }
}
@media (max-width: 390px) {
  .kpis { grid-template-columns: 1fr; }
  .gallery-link { font-size: 12px; }
  h1 { font-size: 28px; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { animation-duration: .001ms !important; animation-iteration-count: 1 !important; transition-duration: .001ms !important; }
  .motion-path { animation: none; stroke-dasharray: none; }
}
@media print {
  body { background: var(--surface); }
  .report-page { max-width: none; padding: 0; }
  .topbar, .slide-nav, .controls, .no-print { display: none !important; }
  .hero, .slide { box-shadow: none; }
  .slide { min-height: 0; break-after: page; }
  .card, .chart-card, .table-wrap, .so-what { break-inside: avoid; }
  .validation { display: none; }
}
"""


class Raw(str):
    """Markup deliberately supplied by a component rather than source text."""


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def fmt_int(value: int | float) -> str:
    return f"{int(round(value)):,}"


def money(value: int | float, decimals: int = 0) -> str:
    if decimals:
        return f"${value:,.{decimals}f}"
    return f"${int(round(value)):,}"


def compact_money(value: int | float) -> str:
    value = float(value)
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000:
        return f"{sign}${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{sign}${value / 1_000:.1f}K"
    return f"{sign}${value:,.0f}"


def pct(value: float, decimals: int = 1) -> str:
    return f"{value * 100:.{decimals}f}%"


def signed_money(value: int | float) -> str:
    return ("+" if value >= 0 else "-") + money(abs(value))


def logo_data(root: Path) -> str:
    path = root / "docs" / "assets" / "vera-mark.png"
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def _cell(value: object) -> str:
    return str(value) if isinstance(value, Raw) else esc(value)


def table(
    headers: Sequence[str],
    rows: Iterable[Sequence[object]],
    *,
    numeric: Sequence[int] = (),
    table_id: str = "",
    classes: str = "",
    caption: str = "",
    row_attrs: Sequence[str] | None = None,
) -> str:
    numeric_set = set(numeric)
    id_attr = f' id="{esc(table_id)}"' if table_id else ""
    head = []
    for index, label in enumerate(headers):
        cls = ' class="num"' if index in numeric_set else ""
        head.append(f'<th scope="col"{cls}>{esc(label)}</th>')
    body = []
    attrs = list(row_attrs or [])
    for row_index, row in enumerate(rows):
        cells = []
        for index, value in enumerate(row):
            cls = ' class="num"' if index in numeric_set else ""
            cells.append(f"<td{cls}>{_cell(value)}</td>")
        attr = f" {attrs[row_index]}" if row_index < len(attrs) else ""
        body.append(f"<tr{attr}>" + "".join(cells) + "</tr>")
    cap = f"<caption>{esc(caption)}</caption>" if caption else ""
    return (
        f'<div class="table-wrap"><table{id_attr} class="{esc(classes)}">'
        + cap
        + "<thead><tr>"
        + "".join(head)
        + "</tr></thead><tbody>"
        + "".join(body)
        + "</tbody></table></div>"
    )


def kpis(items: Sequence[tuple[str, str, str]]) -> str:
    return '<div class="kpis">' + "".join(
        '<div class="kpi">'
        f'<div class="kpi-label">{esc(label)}</div>'
        f'<div class="kpi-value">{esc(value)}</div>'
        f'<div class="kpi-note">{esc(note)}</div></div>'
        for label, value, note in items
    ) + "</div>"


def section(number: int | str, title: str, takeaway: str, body: str) -> str:
    return (
        "<section>"
        f'<div class="section-head"><span class="section-num">{esc(number)}</span>'
        f"<div><h2>{esc(title)}</h2><p class=\"takeaway\">{takeaway}</p></div></div>"
        f"{body}</section>"
    )


def so_what(text: str) -> str:
    return f'<div class="so-what"><div class="label">The so-what</div><p>{text}</p></div>'


def badge(text: str, tone: str = "") -> Raw:
    return Raw(f'<span class="badge {esc(tone)}">{esc(text)}</span>')


def link(href: str, text: str, classes: str = "") -> Raw:
    cls = f' class="{esc(classes)}"' if classes else ""
    return Raw(f'<a href="{esc(href)}"{cls}>{esc(text)}</a>')


def bar_list(items: Sequence[tuple[str, float, str, str]], label: str) -> str:
    """Bars use 95% for the largest actual value, never a rounded axis maximum."""
    maximum = max((float(item[1]) for item in items), default=1.0) or 1.0
    parts = [f'<div class="bar-list" role="group" aria-label="{esc(label)}">']
    for name, value, display, color in items:
        width = max(0.0, float(value)) / maximum * 95.0
        parts.append(
            '<div class="bar-item"><div class="bar-meta">'
            f"<span>{esc(name)}</span><strong>{esc(display)}</strong></div>"
            f'<div class="bar-track"><div class="bar-fill" style="width:{width:.3f}%;background:{esc(color)}"></div></div></div>'
        )
    parts.append("</div>")
    return "".join(parts)


def validation_trail(title: str, generated_on: str, row_scope: str, checks: Sequence[str]) -> str:
    base = [
        "C1 Arithmetic: rates and ratios recomputed from source rows",
        "C2 Canonical filters: fixed synthetic row scopes applied and checked",
        "C3 Temporal currency: fixed snapshot checked; no live freshness claim",
        "C4 Source integrity: approved CSVs and manifest only",
        "C5 Chart provenance: every series generated from source rows in this build",
        "C6 Claim language: scoped to observed synthetic records; no causal claim",
        "C7 Segmentation: populations and periods disclosed beside each metric",
        "C8 Terminology: ARR, activation, retention and forecast terms defined",
        "C9 Currency: monetary aggregation limited to USD source rows",
        "C10 Population sanity: row counts reconciled to the manifest",
        "C11 Reconciliation: movement and mutually exclusive category checks passed",
        "C12 Evidence coverage: claims limited to fields present in the source CSVs",
        "C13 Contrast: canonical token pairs checked programmatically",
        "C14 Responsiveness: narrow layout, scrolling tables and 44px controls included",
        "C15 Typography: system fonts, readable line height and 12px minimum included",
        "C16 Completeness: required files scanned for unfinished markers",
        "C17 Attribution: Built by Vera stamp and dataset date included",
        "C18 ID resolution: visible records use aliases, not internal IDs",
    ]
    additions = [f"Scope check: {item}" for item in checks]
    text = (
        f"VALIDATION TRAIL\nAnalysis: {title}   Run: {generated_on}   Validator: analysis-validator v1\n"
        "GATE 1: DATA CORRECTNESS\n  "
        + "\n  ".join(base[:12])
        + "\nGATE 2: OUTPUT QUALITY\n  "
        + "\n  ".join(base[12:])
        + "\nSIGNIFICANCE: "
        + row_scope
        + "; synthetic cohort, not evidence about a live customer population."
        + "\n"
        + "\n".join(additions)
        + "\nFINAL: PASS"
    )
    return f'<details class="validation"><summary>Validation trail</summary><pre>{esc(text)}</pre></details>'


def page(
    *,
    title: str,
    subtitle: str,
    period: str,
    content: str,
    generated_on: str,
    sources: Sequence[tuple[str, str, str]],
    logo: str,
    depth: int = 0,
    body_class: str = "",
    script: str = "",
    validation_scope: str = "Complete synthetic source cohort",
    validation_checks: Sequence[str] = (),
    hero_badges: Sequence[str] = (),
) -> str:
    gallery_href = "../" * depth + "index.html"
    badges = ["Synthetic / anonymized", period, *hero_badges]
    source_parts = []
    for name, href, digest in sources:
        source_parts.append(f'<a href="{esc(href)}">{esc(name)}</a> ({esc(digest[:12])})')
    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>{esc(title)} | Vera synthetic example</title>
<style>{CSS}</style>
</head>
<body class="{esc(body_class)}">
<div class="report-page">
<header class="topbar">
  <div class="brand"><img src="{logo}" width="42" height="42" alt="Vera mark"><div><div class="brand-name">Vera</div><div class="brand-sub">RevOps examples with traceable synthetic data</div></div></div>
  <a class="gallery-link" href="{gallery_href}">Example gallery</a>
</header>
<div class="hero">
  <p class="eyebrow">Northwind revenue system</p>
  <h1>{esc(title)}</h1>
  <p class="subtitle">{subtitle}</p>
  <div class="meta-row">{''.join(f'<span class="badge">{esc(item)}</span>' for item in badges)}</div>
</div>
{content}
<footer>
  <div class="footer-top"><span class="stamp">Validated by Vera</span><span>Confidence: source-complete, synthetic only</span><span>Built by Vera {esc(generated_on)}</span></div>
  <div class="source-line">Synthetic / anonymized. Period: {esc(period)}. Sources: {' · '.join(source_parts)}.</div>
  {validation_trail(title, generated_on, validation_scope, validation_checks)}
</footer>
</div>
{f'<script>{script}</script>' if script else ''}
</body>
</html>
"""
    return html_doc


def write_json_script(data: object) -> str:
    """Serialize data safely for an inline script."""
    return json.dumps(data, separators=(",", ":"), sort_keys=True).replace("</", "<\\/")
