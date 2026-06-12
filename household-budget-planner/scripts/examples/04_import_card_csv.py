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
    csv_path = os.getenv("HBP_CSV_PATH", "")
    month = os.getenv("HBP_MONTH", "05-2026")
    client = HouseholdBudgetPlannerClient.for_month(month, environment=args.env)
    if csv_path:
        imported = client.load_csv(csv_path)
    else:
        imported = 0
        client.add_transaction(
            date="03-05-2026",
            amount=245.90,
            kind="expense",
            category="food",
            description="Supermarket",
            vendor="Example Market",
            payment_method="credit_card",
            vat_included=True,
        )
        client.add_transaction(
            date="04-05-2026",
            amount=79.90,
            kind="expense",
            category="communications",
            description="Mobile plan",
            vendor="Mobile Provider",
            payment_method="credit_card",
            vat_included=True,
        )
    emit({"environment": args.env, "imported": imported, "summary": client.summary().to_dict()}, args.output)


if __name__ == "__main__":
    main()
