#!/usr/bin/env python3
"""Replacement-home scenario compared with investment-property fallback."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from typing import Any

from mortgage_loan_eligibility_client import MortgageEligibilityClient, calculate_eligibility


def env_float(env: str, key: str, fallback: float) -> float:
    raw = os.getenv(f"MLE_{env.upper()}_{key}", os.getenv(f"MLE_{key}", ""))
    return fallback if raw == "" else float(raw)


def env_int(env: str, key: str, fallback: int) -> int:
    raw = os.getenv(f"MLE_{env.upper()}_{key}", os.getenv(f"MLE_{key}", ""))
    return fallback if raw == "" else int(raw)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
    return p


def print_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    args = parser().parse_args()
    base = {
        "property_value": env_float(args.env, "PROPERTY_VALUE", 3000000),
        "requested_loan_amount": env_float(args.env, "LOAN_AMOUNT", 1950000),
        "net_monthly_income": env_float(args.env, "NET_MONTHLY_INCOME", 42000),
        "existing_monthly_debt": env_float(args.env, "EXISTING_MONTHLY_DEBT", 3500),
        "annual_rate": env_float(args.env, "DEFAULT_ANNUAL_RATE", 5.6),
        "term_years": env_int(args.env, "DEFAULT_TERM_YEARS", 30),
    }
    results = []
    for status in ["replacement_home", "investment_property"]:
        result = calculate_eligibility({**base, "property_status": status})
        results.append(result.to_dict())
    print_json(results)


if __name__ == "__main__":
    main()

