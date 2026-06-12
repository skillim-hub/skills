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
plan = calculate_plan(InstallmentRequest(
    cash_price=env_value("INSTALLMENT_EXAMPLE_PRICE", "9800"),
    down_payment=env_value("INSTALLMENT_EXAMPLE_DOWN_PAYMENT", "2800"),
    installments=int(env_value("INSTALLMENT_EXAMPLE_INSTALLMENTS", "4")),
    first_due_date=env_value("INSTALLMENT_EXAMPLE_FIRST_DATE", "10/08/2026"),
    consumer_context=False,
    label=env_value("INSTALLMENT_EXAMPLE_LABEL", "service quote"),
))
print_payload({"environment": args.env, "scenario": "freelancer_quote", "plan": plan.to_dict()})
