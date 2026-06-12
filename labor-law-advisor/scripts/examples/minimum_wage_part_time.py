#!/usr/bin/env python3
"""Scenario: part-time monthly minimum wage check."""

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
    monthly_salary = float(os.getenv("LABOR_LAW_ADVISOR_MONTHLY_SALARY", "3000"))
    position_fraction = float(os.getenv("LABOR_LAW_ADVISOR_POSITION_FRACTION", "0.5"))
    result = LaborLawAdvisor().minimum_wage(monthly_salary=monthly_salary, position_fraction=position_fraction).to_dict()
    result["environment"] = args.env
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
