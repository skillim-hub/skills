from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from household_budget_planner import HouseholdBudgetPlannerClient, create_sample_plan, extract_vat, format_shekel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("HBP_ENV", "sandbox"))
    parser.add_argument("--output", default=os.getenv("HBP_OUTPUT", ""))
    return parser.parse_args()


def emit(payload: dict, output: str = "") -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if output:
        Path(output).write_text(text + "\n", encoding="utf-8")
    print(text)


def main() -> None:
    args = parse_args()
    month = os.getenv("HBP_MONTH", "05-2026")
    annual_car_insurance = float(os.getenv("HBP_ANNUAL_CAR_INSURANCE", "4800"))
    client = HouseholdBudgetPlannerClient.for_month(month, environment=args.env)
    client.add_transaction(
        date="01-05-2026",
        amount=annual_car_insurance,
        kind="expense",
        category="insurance",
        description="Annual car insurance sinking fund",
        normalize_months=12,
    )
    emit({"environment": args.env, "summary": client.summary().to_dict()}, args.output)


if __name__ == "__main__":
    main()
