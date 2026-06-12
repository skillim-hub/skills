#!/usr/bin/env python3
"""Scenario: protected parental and pregnancy-related status triage."""

from __future__ import annotations

import argparse
import json
import os
from labor_law_advisor_client import LaborLawAdvisor


def env_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("LABOR_LAW_ADVISOR_ENV", "sandbox"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dismissal_or_change = env_bool("LABOR_LAW_ADVISOR_DISMISSAL_OR_CHANGE", "true")
    result = LaborLawAdvisor().parental_rights_triage(
        pregnant=env_bool("LABOR_LAW_ADVISOR_PREGNANT", "true"),
        fertility_treatment=env_bool("LABOR_LAW_ADVISOR_FERTILITY_TREATMENT"),
        returned_from_parental_leave=env_bool("LABOR_LAW_ADVISOR_AFTER_PARENTAL_LEAVE"),
        employer_action="dismissal" if dismissal_or_change else "none",
        months_employed=int(os.getenv("LABOR_LAW_ADVISOR_TENURE_MONTHS", "7")),
    ).to_dict()
    result["environment"] = args.env
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
