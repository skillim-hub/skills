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
    vat_rate = float(os.getenv("HBP_VAT_RATE", "0.18"))
    gross = float(os.getenv("HBP_GROSS_AMOUNT", "11800"))
    client = HouseholdBudgetPlannerClient.for_month(month, vat_rate=vat_rate, environment=args.env)
    client.add_transaction(
        date="10-05-2026",
        amount=gross,
        kind="income",
        category="business",
        description="VAT-inclusive client payment",
        is_business=True,
    )
    client.add_transaction(
        date="11-05-2026",
        amount=590,
        kind="expense",
        category="business",
        description="Software subscription",
        is_business=True,
        vat_included=True,
    )
    breakdown = extract_vat(gross, vat_rate)
    emit(
        {
            "environment": args.env,
            "vat_breakdown": {
                "gross": format_shekel(breakdown.gross_amount),
                "net_before_vat": format_shekel(breakdown.net_before_vat),
                "vat_component": format_shekel(breakdown.vat_component),
            },
            "summary": client.summary().to_dict(),
        },
        args.output,
    )


if __name__ == "__main__":
    main()
