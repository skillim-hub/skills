from __future__ import annotations

import argparse
import json
import os

from installment_calculator import InstallmentRequest, calculate_plan, compare_plans, estimate_refund


def env_value(name: str, default: str) -> str:
    return os.getenv(name, default)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("INSTALLMENT_ENV", "sandbox"))
    return parser.parse_args()


def print_payload(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


args = parse_args()
price = env_value("INSTALLMENT_EXAMPLE_PRICE", "3600")
plans = compare_plans([
    InstallmentRequest(cash_price=price, installments=3, annual_interest_rate="0", first_due_date="05/07/2026", label="3 payments"),
    InstallmentRequest(cash_price=price, installments=6, annual_interest_rate="4.9", first_due_date="05/07/2026", label="6 payments"),
    InstallmentRequest(cash_price=price, installments=12, annual_interest_rate="7.5", per_installment_fee="1.90", first_due_date="05/07/2026", label="12 payments"),
])
print_payload({"environment": args.env, "scenario": "compare_plans", "plans": [plan.to_dict() for plan in plans]})
