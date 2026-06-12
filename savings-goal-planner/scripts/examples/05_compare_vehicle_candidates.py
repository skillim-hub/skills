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
    args = parser("Compare Israeli vehicle candidates.").parse_args()
    horizon = as_int("SGP_MONTHS", 72)
    risk = os.getenv("SGP_RISK", "medium")
    liquidity = os.getenv("SGP_LIQUIDITY", "few_days")
    tax_advantaged = os.getenv("SGP_TAX_ADVANTAGED", "true").lower() in {"1", "true", "yes"}
    candidates = SavingsGoalPlannerClient().recommend_vehicles(
        horizon_months=horizon,
        risk_tolerance=risk,  # type: ignore[arg-type]
        liquidity_need=liquidity,  # type: ignore[arg-type]
        tax_advantaged_available=tax_advantaged,
    )
    print_payload({
        "environment": args.env,
        "scenario": "compare_vehicle_candidates",
        "inputs": {"months": horizon, "risk": risk, "liquidity": liquidity, "tax_advantaged": tax_advantaged},
        "candidates": candidates[:5],
    })


if __name__ == "__main__":
    main()
