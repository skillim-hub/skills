#!/usr/bin/env python3
"""Scenario: collective agreement and extension order triage."""

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
    sector = os.getenv("LABOR_LAW_ADVISOR_SECTOR", "cleaning")
    employer_type = os.getenv("LABOR_LAW_ADVISOR_EMPLOYER_TYPE", "contractor")
    worker_role = os.getenv("LABOR_LAW_ADVISOR_WORKER_ROLE", "cleaner")
    public_sector = employer_type.strip().lower() in {"public", "government", "municipality", "public-sector"}
    result = LaborLawAdvisor().collective_check(
        sector=" ".join(part for part in [sector, employer_type, worker_role] if part),
        public_sector=public_sector,
    ).to_dict()
    result["environment"] = args.env
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
