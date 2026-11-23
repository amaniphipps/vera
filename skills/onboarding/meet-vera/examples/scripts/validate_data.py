#!/usr/bin/env python3
"""Validate source data and write the canonical metric manifest."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
MANIFEST = DATA / "manifest.json"
GENERATED_ON = "2026-11-23"
SEED = 20261123


def rows(name: str) -> list[dict]:
    with (DATA / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def number(value: str) -> int:
    return int(value)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    accounts = rows("crm-accounts.csv")
    contacts = rows("crm-contacts.csv")
    opportunities = rows("crm-opportunities.csv")
    history = rows("crm-stage-history.csv")
    activities = rows("crm-activities.csv")
    arr = rows("arr-rollforward.csv")
    activation = rows("activation-users.csv")
    quotas = rows("quota-targets.csv")

    account_ids = [r["account_id"] for r in accounts]
    account_set = set(account_ids)
    arr_by_id = {r["account_id"]: r for r in arr}
    opp_by_id = {r["opportunity_id"]: r for r in opportunities}
    require(len(account_ids) == len(account_set) == 1050, "Expected 1,050 unique accounts")
    require(len(arr) == len(arr_by_id) == 1050, "Expected 1,050 unique ARR rows")
    require(account_set == set(arr_by_id), "Account and ARR keys differ")
    require(len({r["contact_id"] for r in contacts}) == len(contacts) == 2100, "Expected 2,100 unique contacts")
    require(all(r["account_id"] in account_set for r in contacts), "Orphan contact")
    require(all(re.fullmatch(r"contact\d{6}@example\.invalid", r["email"]) for r in contacts), "Unexpected contact email")
    require(len(opp_by_id) == len(opportunities) == 600, "Expected 600 opportunities")
    require(all(r["account_id"] in account_set for r in opportunities), "Orphan opportunity")
    require(all(r["opportunity_id"] in opp_by_id and r["account_id"] in account_set for r in history), "Orphan stage history")
    require(all(r["opportunity_id"] in opp_by_id and r["account_id"] in account_set for r in activities), "Orphan activity")
    require(len(activities) == 3000, "Expected 3,000 activities")
    latest_activity = {}
    for activity in activities:
        if activity["outcome"] != "Scheduled":
            latest_activity[activity["opportunity_id"]] = max(latest_activity.get(activity["opportunity_id"], ""), activity["activity_date"])
    require(all(opp["last_activity_date"] == latest_activity.get(opp["opportunity_id"], "") for opp in opportunities), "Opportunity last-activity dates do not match activity records")
    require(len(activation) == 2400, "Expected 2,400 activation users")
    require(all(r["account_id"] in account_set for r in activation), "Orphan activation user")
    require(len(quotas) == 8, "Expected 8 quota rows")

    category_counts = Counter(r["movement_category"] for r in arr)
    require(category_counts == Counter({"Flat": 670, "Expansion": 150, "Contraction": 100, "Churn": 50, "New": 80}), f"Unexpected ARR movement counts: {category_counts}")
    for row in arr:
        start, new, expansion = number(row["starting_arr"]), number(row["new_arr"]), number(row["expansion_arr"])
        contraction, churn, ending = number(row["contraction_arr"]), number(row["churn_arr"]), number(row["ending_arr"])
        require(ending == start + new + expansion - contraction - churn, f"ARR mismatch: {row['account_id']}")
        require(start >= 0 and new >= 0 and expansion >= 0 and contraction >= 0 and churn >= 0 and ending >= 0, f"Negative ARR: {row['account_id']}")
        if row["movement_category"] == "New":
            require(start == 0 and new == ending and ending > 0, f"Invalid new movement: {row['account_id']}")
        elif row["movement_category"] == "Churn":
            require(start == churn and ending == 0, f"Invalid churn movement: {row['account_id']}")
        elif row["movement_category"] == "Flat":
            require(start == ending and start > 0, f"Invalid flat movement: {row['account_id']}")
        elif row["movement_category"] == "Expansion":
            require(expansion > 0 and ending > start > 0, f"Invalid expansion: {row['account_id']}")
        elif row["movement_category"] == "Contraction":
            require(contraction > 0 and start > ending > 0, f"Invalid contraction: {row['account_id']}")

    ending_active = sum(number(r["ending_arr"]) > 0 for r in arr)
    starting_active = sum(number(r["starting_arr"]) > 0 for r in arr)
    require(ending_active == 1000, "Expected 1,000 ending active customers")
    require(starting_active == 970, "Expected 970 starting active customers")
    require(sum(r["lifecycle_status"] == "Active" for r in accounts) == 1000, "Account active status mismatch")
    require(sum(r["lifecycle_status"] == "Churned" for r in accounts) == 50, "Account churn status mismatch")

    open_opps = [r for r in opportunities if r["forecast_category"]]
    closed = [r for r in opportunities if not r["forecast_category"]]
    require(len(open_opps) == 200, "Expected 200 open opportunities")
    require(len(closed) == 400, "Expected 400 closed opportunities")
    require(Counter(r["forecast_category"] for r in open_opps) == Counter({"Commit": 60, "Best Case": 60, "Pipeline": 80}), "Open forecast counts differ")
    require(all(r["stage"] in {"Discovery", "Validation", "Proposal", "Negotiation"} for r in open_opps), "Open stage mismatch")
    require(all(r["stage"] in {"Closed Won", "Closed Lost"} for r in closed), "Closed stage mismatch")
    require(all(r["close_date"] >= "2026-11-24" for r in open_opps), "Open close date precedes dataset date")
    require(all(r["created_date"] <= GENERATED_ON for r in opportunities), "Future created date")

    q3_won_by_account = defaultdict(int)
    for opp in closed:
        if opp["period"] == "2026-Q3" and opp["stage"] == "Closed Won":
            q3_won_by_account[opp["account_id"]] += number(opp["expected_arr_usd"])
    expected_q3 = {r["account_id"]: number(r["new_arr"]) + number(r["expansion_arr"]) for r in arr if r["movement_category"] in {"New", "Expansion"}}
    require(dict(q3_won_by_account) == expected_q3, "Q3 closed-won ARR does not reconcile to new + expansion")

    arr_sums = {key: sum(number(r[key]) for r in arr) for key in ["starting_arr", "new_arr", "expansion_arr", "contraction_arr", "churn_arr", "ending_arr"]}
    require(arr_sums["ending_arr"] == arr_sums["starting_arr"] + arr_sums["new_arr"] + arr_sums["expansion_arr"] - arr_sums["contraction_arr"] - arr_sums["churn_arr"], "Aggregate ARR does not reconcile")
    start = arr_sums["starting_arr"]
    grr = (start - arr_sums["contraction_arr"] - arr_sums["churn_arr"]) / start
    nrr = (start + arr_sums["expansion_arr"] - arr_sums["contraction_arr"] - arr_sums["churn_arr"]) / start

    forecast_sums = {category: sum(number(r["expected_arr_usd"]) for r in open_opps if r["forecast_category"] == category) for category in ["Commit", "Best Case", "Pipeline"]}
    q4_won = sum(number(r["expected_arr_usd"]) for r in closed if r["period"] == "2026-Q4" and r["stage"] == "Closed Won")
    commit_view = q4_won + forecast_sums["Commit"]
    best_case_view = commit_view + forecast_sums["Best Case"]
    full_view = best_case_view + forecast_sums["Pipeline"]

    cohorts = {}
    for cohort in sorted({r["cohort_week"] for r in activation}):
        subset = [r for r in activation if r["cohort_week"] == cohort]
        activated = sum(r["activated"] == "true" for r in subset)
        retained = sum(r["retained_w2"] == "true" for r in subset)
        require(retained <= activated <= len(subset), f"Invalid activation cohort {cohort}")
        require(all(r["activated"] == "true" for r in subset if r["retained_w2"] == "true"), f"Retained non-activated user in {cohort}")
        cohorts[cohort] = {"signups": len(subset), "activated": activated, "retained_w2": retained}
    activated_total = sum(r["activated"] == "true" for r in activation)
    retained_total = sum(r["retained_w2"] == "true" for r in activation)
    require((len(activation), activated_total, retained_total) == (2400, 1320, 792), "Activation totals differ")

    stage_counts = Counter(r["stage"] for r in open_opps)
    won = sum(r["stage"] == "Closed Won" for r in closed)
    lost = sum(r["stage"] == "Closed Lost" for r in closed)
    table_rows = {
        "crm-accounts.csv": len(accounts),
        "crm-contacts.csv": len(contacts),
        "crm-opportunities.csv": len(opportunities),
        "crm-stage-history.csv": len(history),
        "crm-activities.csv": len(activities),
        "arr-rollforward.csv": len(arr),
        "activation-users.csv": len(activation),
        "quota-targets.csv": len(quotas),
        "pdf-invoice.csv": len(rows("pdf-invoice.csv")),
        "pdf-quarterly-sales.csv": len(rows("pdf-quarterly-sales.csv")),
    }
    source_files = sorted(table_rows) + ["mock-pipeline.csv"]
    hashes = {}
    for name in source_files:
        path = BASE / name if name == "mock-pipeline.csv" else DATA / name
        hashes[name] = sha256(path)

    manifest = {
        "dataset": "Northwind synthetic CRM and ARR",
        "version": "1.0.0",
        "seed": SEED,
        "generated_on": GENERATED_ON,
        "currency": "USD",
        "synthetic": True,
        "anonymized": True,
        "periods": {"arr_rollforward": "2026-Q3", "pipeline_forecast": "2026-Q4"},
        "tables": table_rows,
        "total_linked_records": sum(table_rows.values()),
        "arr": {
            **arr_sums,
            "starting_active_customers": starting_active,
            "ending_active_customers": ending_active,
            "movement_counts": dict(sorted(category_counts.items())),
            "net_arr_added": arr_sums["ending_arr"] - start,
            "grr": round(grr, 6),
            "nrr": round(nrr, 6),
        },
        "pipeline": {
            "open_deals": len(open_opps),
            "closed_deals": len(closed),
            "open_by_forecast": dict(Counter(r["forecast_category"] for r in open_opps)),
            "open_by_stage": dict(sorted(stage_counts.items())),
            "open_expected_arr_by_forecast": forecast_sums,
            "open_expected_arr_total": sum(forecast_sums.values()),
            "q4_closed_won_arr": q4_won,
            "commit_view": commit_view,
            "best_case_view": best_case_view,
            "full_pipeline_view": full_view,
            "closed_won": won,
            "closed_lost": lost,
            "closed_win_rate": round(won / (won + lost), 6),
        },
        "activation": {
            "signups": len(activation),
            "activated": activated_total,
            "retained_w2": retained_total,
            "activation_rate": round(activated_total / len(activation), 6),
            "retention_of_activated": round(retained_total / activated_total, 6),
            "overall_retention": round(retained_total / len(activation), 6),
            "cohorts": cohorts,
        },
        "source_sha256": hashes,
        "validation": {
            "unique_primary_keys": True,
            "zero_orphaned_foreign_keys": True,
            "arr_rows_reconcile": True,
            "q3_crm_arr_reconciles": True,
            "anonymized_email_domain_only": True,
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "accounts": len(accounts), "ending_active": ending_active, "open_deals": len(open_opps), "closed_deals": len(closed), "total_linked_records": sum(table_rows.values()), "starting_arr": start, "ending_arr": arr_sums["ending_arr"], "grr": round(grr, 6), "nrr": round(nrr, 6), "open_expected_arr": sum(forecast_sums.values())}, indent=2))


if __name__ == "__main__":
    main()
