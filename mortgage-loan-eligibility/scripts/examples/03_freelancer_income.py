#!/usr/bin/env python3
"""Freelancer income stabilization from verified monthly records."""

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
    request = {
        "property_value": env_float(args.env, "PROPERTY_VALUE", 1800000),
        "requested_loan_amount": env_float(args.env, "LOAN_AMOUNT", 1100000),
        "property_status": "single_home",
        "income_records": [
            {"period": "2025-01", "net_income": 18500, "verified": True},
            {"period": "2025-02", "net_income": 21000, "verified": True},
            {"period": "2025-03", "net_income": 16500, "verified": True},
            {"period": "2025-04", "net_income": 23000, "verified": True},
            {"period": "2025-05", "net_income": 19000, "verified": True},
            {"period": "2025-06", "net_income": 19500, "verified": True},
        ],
        "existing_monthly_debt": env_float(args.env, "EXISTING_MONTHLY_DEBT", 2200),
        "annual_rate": env_float(args.env, "DEFAULT_ANNUAL_RATE", 5.4),
        "term_years": env_int(args.env, "DEFAULT_TERM_YEARS", 25),
    }
    print_json(MortgageEligibilityClient().calculate(request).to_dict())


if __name__ == "__main__":
    main()

