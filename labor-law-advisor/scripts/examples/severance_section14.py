#!/usr/bin/env python3
"""Scenario: statutory severance estimate with Section 14 balance."""

from __future__ import annotations

import argparse
import json
import os
from labor_law_advisor_client import LaborLawAdvisor


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("LABOR_LAW_ADVISOR_ENV", "sandbox"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    monthly_salary = float(os.getenv("LABOR_LAW_ADVISOR_MONTHLY_SALARY", "12000"))
    years = float(os.getenv("LABOR_LAW_ADVISOR_TENURE_YEARS", "3"))
    months = float(os.getenv("LABOR_LAW_ADVISOR_TENURE_MONTHS", "4"))
    section14_balance = float(os.getenv("LABOR_LAW_ADVISOR_SECTION14_BALANCE", "35000"))
    result = LaborLawAdvisor().severance(
        monthly_salary=monthly_salary,
        years=years,
        months=months,
        section14_balance=section14_balance,
    ).to_dict()
    result["environment"] = args.env
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
