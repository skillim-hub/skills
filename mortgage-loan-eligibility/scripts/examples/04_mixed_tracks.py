#!/usr/bin/env python3
"""Mixed mortgage tracks with separate rates and equal total principal."""

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
        "property_value": env_float(args.env, "PROPERTY_VALUE", 2500000),
        "requested_loan_amount": env_float(args.env, "LOAN_AMOUNT", 1500000),
        "property_status": "single_home",
        "net_monthly_income": env_float(args.env, "NET_MONTHLY_INCOME", 33000),
        "existing_monthly_debt": env_float(args.env, "EXISTING_MONTHLY_DEBT", 1500),
        "tracks": [
            {"name": "fixed_unlinked", "principal": 500000, "annual_rate": 4.9, "term_years": 25},
            {"name": "prime", "principal": 500000, "annual_rate": 5.4, "term_years": 25},
            {"name": "variable_cpi", "principal": 500000, "annual_rate": 4.7, "term_years": 25},
        ],
    }
    print_json(calculate_eligibility(request).to_dict())


if __name__ == "__main__":
    main()

