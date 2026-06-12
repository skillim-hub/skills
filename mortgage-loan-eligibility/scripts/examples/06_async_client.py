#!/usr/bin/env python3
"""Async client facade for integration code that already uses asyncio."""

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


async def run(env: str) -> dict[str, Any]:
    client = MortgageEligibilityClient(default_annual_rate=env_float(env, "DEFAULT_ANNUAL_RATE", 5.0))
    result = await client.acalculate({
        "property_value": env_float(env, "PROPERTY_VALUE", 2000000),
        "requested_loan_amount": env_float(env, "LOAN_AMOUNT", 1000000),
        "property_status": "investment_property",
        "net_monthly_income": env_float(env, "NET_MONTHLY_INCOME", 42000),
        "term_years": env_int(env, "DEFAULT_TERM_YEARS", 20),
    })
    return result.to_dict()


def main() -> None:
    args = parser().parse_args()
    print_json(asyncio.run(run(args.env)))


if __name__ == "__main__":
    main()

