#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from typing import Any

from savings_goal_planner import GoalRequest, RetirementRequest, SavingsGoalPlannerClient


def parser(description: str) -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser(description=description)
    arg_parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("SGP_ENV", "sandbox"))
    return arg_parser


def as_float(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)))


def as_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def print_payload(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))

def main() -> None:
    args = parser("Plan a business tax reserve.").parse_args()
    request = GoalRequest(
        goal_name=os.getenv("SGP_GOAL_NAME", "Quarterly VAT and tax reserve"),
        target_amount=as_float("SGP_TARGET", 51000),
        months=as_int("SGP_MONTHS", 3),
        current_savings=as_float("SGP_CURRENT_SAVINGS", 12000),
        current_monthly_savings=as_float("SGP_CURRENT_MONTHLY", 8000),
        vehicle_key=os.getenv("SGP_VEHICLE", "cash_bank"),
    )
    result = SavingsGoalPlannerClient().calculate_goal(request)
    print_payload({"environment": args.env, "scenario": "business_tax_reserve", "result": result.to_dict()})


if __name__ == "__main__":
    main()
