#!/usr/bin/env python3
"""Scenario: daily overtime calculation."""

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
    hourly_rate = float(os.getenv("LABOR_LAW_ADVISOR_HOURLY_RATE", "40"))
    daily_hours = float(os.getenv("LABOR_LAW_ADVISOR_DAILY_HOURS", "11"))
    daily_threshold = float(os.getenv("LABOR_LAW_ADVISOR_DAILY_THRESHOLD", "8.6"))
    result = LaborLawAdvisor().overtime(
        hourly_rate=hourly_rate,
        daily_hours=daily_hours,
        daily_threshold=daily_threshold,
    ).to_dict()
    result["environment"] = args.env
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
