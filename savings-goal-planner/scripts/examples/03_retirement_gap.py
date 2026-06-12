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
    args = parser("Calculate a simplified retirement gap.").parse_args()
    request = RetirementRequest(
        current_age=as_float("SGP_CURRENT_AGE", 42),
        retirement_age=as_float("SGP_RETIREMENT_AGE", 67),
        life_expectancy=as_float("SGP_LIFE_EXPECTANCY", 95),
        desired_monthly_spending_today=as_float("SGP_MONTHLY_SPENDING", 14000),
        expected_monthly_pension_today=as_float("SGP_EXPECTED_PENSION", as_float("SGP_STATE_PENSION", 7000)),
        current_retirement_savings=as_float("SGP_CURRENT_SAVINGS", 180000),
        annual_real_return_accumulation=as_float("SGP_ACCUMULATION_RETURN", 0.04),
        annual_real_return_retirement=as_float("SGP_RETIREMENT_RETURN", 0.025),
    )
    result = SavingsGoalPlannerClient().calculate_retirement(request)
    print_payload({"environment": args.env, "scenario": "retirement_gap", "result": result.to_dict()})


if __name__ == "__main__":
    main()
