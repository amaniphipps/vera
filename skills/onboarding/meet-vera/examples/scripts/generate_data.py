#!/usr/bin/env python3
"""Generate Vera's deterministic, anonymized Northwind example datasets."""
from __future__ import annotations

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 20261123
GENERATED_ON = date(2026, 11, 23)
BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
RNG = random.Random(SEED)

SEGMENTS = ["SMB", "Mid-Market", "Enterprise"]
INDUSTRIES = ["Software", "Manufacturing", "Healthcare", "Financial Services", "Retail", "Education", "Logistics", "Professional Services"]
REGIONS = [("North America", "United States"), ("North America", "Canada"), ("Europe", "United Kingdom"), ("Europe", "Germany"), ("APAC", "Australia")]
PLANS = ["Starter", "Growth", "Scale", "Enterprise"]
SOURCES = ["Outbound", "Inbound", "Partner", "Referral", "Event"]
PRODUCTS = ["Core Platform", "Analytics", "Automation", "Collaboration"]
OPEN_STAGES = ["Discovery", "Validation", "Proposal", "Negotiation"]
ALL_OPEN_STAGES = ["Discovery", "Validation", "Proposal", "Negotiation"]
LOSS_REASONS = ["Budget", "Timing", "Competitor", "No decision", "Security review"]
WIN_REASONS = ["Product fit", "Expansion success", "ROI case", "Team adoption"]


def iso(value: date) -> str:
    return value.isoformat()


def random_date(start: date, end: date) -> date:
    return start + timedelta(days=RNG.randint(0, (end - start).days))


def base_arr(segment: str) -> int:
    if segment == "SMB":
        value = RNG.lognormvariate(10.25, 0.45)
        return int(max(6000, min(75000, round(value / 100) * 100)))
    if segment == "Mid-Market":
        value = RNG.lognormvariate(11.25, 0.45)
        return int(max(30000, min(240000, round(value / 100) * 100)))
    value = RNG.lognormvariate(12.35, 0.42)
    return int(max(90000, min(650000, round(value / 100) * 100)))


def write_csv(name: str, fields: list[str], rows: list[dict]) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    with (DATA / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    categories = (["Flat"] * 670 + ["Expansion"] * 150 + ["Contraction"] * 100 + ["Churn"] * 50 + ["New"] * 80)
    RNG.shuffle(categories)
    accounts: list[dict] = []
    arr_rows: list[dict] = []
    account_by_id: dict[str, dict] = {}
    arr_by_id: dict[str, dict] = {}

    for index, category in enumerate(categories, 1):
        account_id = f"acct_{index:04d}"
        segment = RNG.choices(SEGMENTS, weights=[45, 35, 20], k=1)[0]
        region, country = RNG.choice(REGIONS)
        owner_num = RNG.randint(1, 8)
        owner_id = f"owner_{owner_num:02d}"
        start_arr = base_arr(segment) if category != "New" else 0
        new_arr = expansion_arr = contraction_arr = churn_arr = 0
        if category == "New":
            new_arr = base_arr(segment)
            ending_arr = new_arr
        elif category == "Expansion":
            expansion_arr = max(1000, round(start_arr * RNG.uniform(0.06, 0.36) / 100) * 100)
            ending_arr = start_arr + expansion_arr
        elif category == "Contraction":
            contraction_arr = max(1000, round(start_arr * RNG.uniform(0.05, 0.31) / 100) * 100)
            contraction_arr = min(contraction_arr, start_arr - 1000)
            ending_arr = start_arr - contraction_arr
        elif category == "Churn":
            churn_arr = start_arr
            ending_arr = 0
        else:
            ending_arr = start_arr
        previous_plan = RNG.choices(PLANS, weights=[25, 40, 25, 10], k=1)[0]
        current_plan = previous_plan
        if category == "Expansion" and previous_plan != "Enterprise":
            current_plan = PLANS[min(PLANS.index(previous_plan) + 1, len(PLANS) - 1)]
        elif category == "Contraction" and previous_plan != "Starter":
            current_plan = PLANS[PLANS.index(previous_plan) - 1]
        created = random_date(date(2022, 1, 1), date(2026, 6, 30))
        customer_since = created if category != "New" else random_date(date(2026, 7, 1), date(2026, 9, 30))
        account = {
            "account_id": account_id,
            "account_alias": f"Account {index:04d}",
            "lifecycle_status": "Churned" if ending_arr == 0 else "Active",
            "segment": segment,
            "industry": RNG.choice(INDUSTRIES),
            "region": region,
            "country": country,
            "owner_id": owner_id,
            "owner_alias": f"Owner {owner_num:02d}",
            "plan_tier": current_plan,
            "billing_frequency": RNG.choice(["Monthly", "Annual"]),
            "currency": "USD",
            "account_created_date": iso(created),
            "customer_since_date": iso(customer_since),
            "health_score": RNG.randint(35, 98) if ending_arr else RNG.randint(10, 45),
            "last_activity_date": iso(random_date(date(2026, 10, 1), GENERATED_ON)),
            "acquisition_source": RNG.choice(SOURCES),
            "movement_category": category,
        }
        arr = {
            "account_id": account_id,
            "period": "2026-Q3",
            "starting_arr": start_arr,
            "new_arr": new_arr,
            "expansion_arr": expansion_arr,
            "contraction_arr": contraction_arr,
            "churn_arr": churn_arr,
            "ending_arr": ending_arr,
            "movement_category": category,
            "previous_plan_tier": previous_plan,
            "current_plan_tier": current_plan,
            "currency": "USD",
        }
        accounts.append(account)
        arr_rows.append(arr)
        account_by_id[account_id] = account
        arr_by_id[account_id] = arr

    account_fields = ["account_id", "account_alias", "lifecycle_status", "segment", "industry", "region", "country", "owner_id", "owner_alias", "plan_tier", "billing_frequency", "currency", "account_created_date", "customer_since_date", "health_score", "last_activity_date", "acquisition_source", "movement_category"]
    arr_fields = ["account_id", "period", "starting_arr", "new_arr", "expansion_arr", "contraction_arr", "churn_arr", "ending_arr", "movement_category", "previous_plan_tier", "current_plan_tier", "currency"]
    write_csv("crm-accounts.csv", account_fields, accounts)
    write_csv("arr-rollforward.csv", arr_fields, arr_rows)

    contacts: list[dict] = []
    roles = ["Economic buyer", "Champion", "Operations", "Finance", "Technical reviewer", "Executive sponsor"]
    for account in accounts:
        for position in (1, 2):
            number = len(contacts) + 1
            contacts.append({
                "contact_id": f"contact_{number:06d}",
                "account_id": account["account_id"],
                "contact_alias": f"Contact {number:06d}",
                "role": "Primary champion" if position == 1 else RNG.choice(roles),
                "email": f"contact{number:06d}@example.invalid",
                "is_primary": "true" if position == 1 else "false",
                "last_engagement_date": account["last_activity_date"],
            })
    write_csv("crm-contacts.csv", ["contact_id", "account_id", "contact_alias", "role", "email", "is_primary", "last_engagement_date"], contacts)

    opportunities: list[dict] = []
    internal_meta: dict[str, dict] = {}

    def add_opportunity(account: dict, stage: str, close_date: date, expected_arr: int, *, forecast: str = "", outcome: str = "", period: str) -> dict:
        number = len(opportunities) + 1
        opp_id = f"opp_{number:04d}"
        created = random_date(close_date - timedelta(days=105), min(close_date - timedelta(days=20), GENERATED_ON))
        if stage == "Closed Won":
            probability, risk = 100, "Closed"
        elif stage == "Closed Lost":
            probability, risk = 0, "Closed"
        else:
            probability = {"Discovery": 15, "Validation": 30, "Proposal": 55, "Negotiation": 75}[stage] + RNG.choice([-5, 0, 5])
            risk = RNG.choices(["On track", "Watch", "At risk"], weights=[55, 30, 15], k=1)[0]
        opp = {
            "opportunity_id": opp_id,
            "account_id": account["account_id"],
            "opportunity_alias": f"Opportunity {number:04d}",
            "owner_id": account["owner_id"],
            "owner_alias": account["owner_alias"],
            "stage": stage,
            "forecast_category": forecast,
            "amount_usd": expected_arr * RNG.randint(1, 3),
            "expected_arr_usd": expected_arr,
            "probability": probability,
            "created_date": iso(created),
            "close_date": iso(close_date),
            "last_activity_date": iso(min(close_date, GENERATED_ON)),
            "next_step_date": iso(close_date - timedelta(days=7)) if not outcome else "",
            "acquisition_source": account["acquisition_source"],
            "product_family": RNG.choice(PRODUCTS),
            "opportunity_type": RNG.choice(["Expansion", "Renewal", "New Product"]),
            "risk_status": risk,
            "next_step": f"Review {opp_id} next action" if not outcome else "",
            "win_reason": RNG.choice(WIN_REASONS) if outcome == "Won" else "",
            "loss_reason": RNG.choice(LOSS_REASONS) if outcome == "Lost" else "",
            "competitor_alias": f"Competitor {RNG.choice(['A', 'B', 'C'])}" if outcome == "Lost" else "",
            "period": period,
        }
        opportunities.append(opp)
        internal_meta[opp_id] = {"created": created, "close": close_date, "outcome": outcome, "current_stage": stage}
        return opp

    for arr in arr_rows:
        if arr["movement_category"] not in ("New", "Expansion"):
            continue
        account = account_by_id[arr["account_id"]]
        amount = arr["new_arr"] or arr["expansion_arr"]
        close_date = datetime.strptime(account["customer_since_date"], "%Y-%m-%d").date() if arr["movement_category"] == "New" else random_date(date(2026, 7, 1), date(2026, 9, 30))
        add_opportunity(account, "Closed Won", close_date, amount, outcome="Won", period="2026-Q3")

    active_accounts = [a for a in accounts if a["lifecycle_status"] == "Active"]
    for _ in range(80):
        account = RNG.choice(active_accounts)
        add_opportunity(account, "Closed Lost", random_date(date(2026, 7, 1), date(2026, 9, 30)), base_arr(account["segment"]), outcome="Lost", period="2026-Q3")
    for _ in range(30):
        account = RNG.choice(active_accounts)
        add_opportunity(account, "Closed Won", random_date(date(2026, 10, 1), date(2026, 11, 20)), base_arr(account["segment"]), outcome="Won", period="2026-Q4")
    for _ in range(60):
        account = RNG.choice(active_accounts)
        add_opportunity(account, "Closed Lost", random_date(date(2026, 10, 1), date(2026, 11, 20)), base_arr(account["segment"]), outcome="Lost", period="2026-Q4")

    forecast_categories = ["Commit"] * 60 + ["Best Case"] * 60 + ["Pipeline"] * 80
    RNG.shuffle(forecast_categories)
    for forecast in forecast_categories:
        account = RNG.choice(active_accounts)
        if forecast == "Commit":
            stage = RNG.choices(["Negotiation", "Proposal"], weights=[70, 30], k=1)[0]
        elif forecast == "Best Case":
            stage = RNG.choices(["Proposal", "Negotiation"], weights=[60, 40], k=1)[0]
        else:
            stage = RNG.choices(["Discovery", "Validation", "Proposal"], weights=[40, 40, 20], k=1)[0]
        add_opportunity(account, stage, random_date(date(2026, 11, 24), date(2026, 12, 31)), base_arr(account["segment"]), forecast=forecast, period="2026-Q4")

    opp_fields = ["opportunity_id", "account_id", "opportunity_alias", "owner_id", "owner_alias", "stage", "forecast_category", "amount_usd", "expected_arr_usd", "probability", "created_date", "close_date", "last_activity_date", "next_step_date", "acquisition_source", "product_family", "opportunity_type", "risk_status", "next_step", "win_reason", "loss_reason", "competitor_alias", "period"]
    write_csv("crm-opportunities.csv", opp_fields, opportunities)

    stage_history: list[dict] = []
    for opp in opportunities:
        meta = internal_meta[opp["opportunity_id"]]
        if meta["outcome"] == "Won":
            stages = ALL_OPEN_STAGES + ["Closed Won"]
        elif meta["outcome"] == "Lost":
            stages = ALL_OPEN_STAGES[: RNG.randint(1, 4)] + ["Closed Lost"]
        else:
            stages = ALL_OPEN_STAGES[: ALL_OPEN_STAGES.index(meta["current_stage"]) + 1]
        start = meta["created"]
        end = meta["close"] if meta["outcome"] else min(meta["close"], GENERATED_ON)
        span = max(1, (end - start).days)
        for sequence, stage in enumerate(stages, 1):
            entered = start + timedelta(days=round((sequence - 1) * span / len(stages)))
            if not meta["outcome"] and sequence == len(stages):
                exited_value = ""
            else:
                exited = start + timedelta(days=round(sequence * span / len(stages))) if sequence < len(stages) else end
                exited_value = iso(exited)
            stage_history.append({
                "stage_history_id": f"hist_{len(stage_history) + 1:06d}",
                "opportunity_id": opp["opportunity_id"],
                "account_id": opp["account_id"],
                "stage": stage,
                "sequence": sequence,
                "entered_at": iso(entered),
                "exited_at": exited_value,
                "owner_id": opp["owner_id"],
            })
    write_csv("crm-stage-history.csv", ["stage_history_id", "opportunity_id", "account_id", "stage", "sequence", "entered_at", "exited_at", "owner_id"], stage_history)

    activities: list[dict] = []
    for _ in range(3000):
        opp = RNG.choice(opportunities)
        meta = internal_meta[opp["opportunity_id"]]
        activity_date = random_date(meta["created"], min(meta["close"], GENERATED_ON))
        activities.append({
            "activity_id": f"act_{len(activities) + 1:06d}",
            "account_id": opp["account_id"],
            "opportunity_id": opp["opportunity_id"],
            "owner_id": opp["owner_id"],
            "activity_type": RNG.choice(["Email", "Call", "Meeting", "Note"]),
            "activity_date": iso(activity_date),
            "outcome": RNG.choice(["Completed", "Completed", "No Response", "Scheduled"]),
            "subject_alias": f"Activity {len(activities) + 1:06d}",
        })
    write_csv("crm-activities.csv", ["activity_id", "account_id", "opportunity_id", "owner_id", "activity_type", "activity_date", "outcome", "subject_alias"], activities)

    latest_activity: dict[str, str] = {}
    for activity in activities:
        opp_id = activity["opportunity_id"]
        if activity["outcome"] != "Scheduled":
            latest_activity[opp_id] = max(latest_activity.get(opp_id, ""), activity["activity_date"])
    for opp in opportunities:
        opp["last_activity_date"] = latest_activity.get(opp["opportunity_id"], "")
    write_csv("crm-opportunities.csv", opp_fields, opportunities)

    activation: list[dict] = []
    cohorts = [(1, 612, 374, 241), (2, 598, 331, 204), (3, 604, 318, 181), (4, 586, 297, 166)]
    for week, signups, activated_count, retained_count in cohorts:
        start = date(2026, 9, 28) + timedelta(days=(week - 1) * 7)
        activated_indices = set(RNG.sample(range(signups), activated_count))
        retained_indices = set(RNG.sample(sorted(activated_indices), retained_count))
        for index in range(signups):
            number = len(activation) + 1
            signup = start + timedelta(days=RNG.randint(0, 6))
            activated = index in activated_indices
            retained = index in retained_indices
            activation.append({
                "user_id": f"user_{number:06d}",
                "account_id": RNG.choice(active_accounts)["account_id"],
                "user_alias": f"User {number:06d}",
                "cohort_week": f"2026-W{40 + week - 1}",
                "signup_date": iso(signup),
                "activated": "true" if activated else "false",
                "activated_date": iso(signup + timedelta(days=RNG.randint(0, 7))) if activated else "",
                "retained_w2": "true" if retained else "false",
                "acquisition_source": RNG.choice(SOURCES),
            })
    write_csv("activation-users.csv", ["user_id", "account_id", "user_alias", "cohort_week", "signup_date", "activated", "activated_date", "retained_w2", "acquisition_source"], activation)

    quotas: list[dict] = []
    for number in range(1, 9):
        quotas.append({
            "owner_id": f"owner_{number:02d}",
            "owner_alias": f"Owner {number:02d}",
            "period": "2026-Q4",
            "quota_usd": 500000 + number * 50000,
            "tier1_threshold": 0.8,
            "tier1_rate": 0.08,
            "tier2_threshold": 1.0,
            "tier2_rate": 0.12,
            "tier3_rate": 0.18,
            "currency": "USD",
        })
    write_csv("quota-targets.csv", ["owner_id", "owner_alias", "period", "quota_usd", "tier1_threshold", "tier1_rate", "tier2_threshold", "tier2_rate", "tier3_rate", "currency"], quotas)

    write_csv("pdf-invoice.csv", ["invoice_id", "item", "quantity", "unit_price_usd", "line_total_usd"], [
        {"invoice_id": "12345", "item": "Widget", "quantity": 2, "unit_price_usd": 50, "line_total_usd": 100},
        {"invoice_id": "12345", "item": "Gadget", "quantity": 1, "unit_price_usd": 75, "line_total_usd": 75},
    ])
    write_csv("pdf-quarterly-sales.csv", ["product", "q1_units", "q2_units", "q3_units", "q4_units"], [
        {"product": "Widgets", "q1_units": 120, "q2_units": 135, "q3_units": 142, "q4_units": 158},
        {"product": "Gadgets", "q1_units": 85, "q2_units": 92, "q3_units": 98, "q4_units": 105},
    ])

    open_rows = [o for o in opportunities if o["forecast_category"]]
    with (BASE / "mock-pipeline.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["deal", "stage", "value_usd", "close_date", "owner", "risk"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for opp in open_rows:
            writer.writerow({"deal": opp["opportunity_alias"], "stage": opp["stage"], "value_usd": opp["expected_arr_usd"], "close_date": opp["close_date"], "owner": opp["owner_alias"], "risk": opp["risk_status"].lower().replace(" ", "-")})

    print(f"Generated {len(accounts)} accounts, {len(open_rows)} open opportunities, {len(opportunities) - len(open_rows)} closed opportunities")
    print(f"Generated {len(contacts)} contacts, {len(stage_history)} stage rows, {len(activities)} activities, {len(activation)} activation users")


if __name__ == "__main__":
    main()
