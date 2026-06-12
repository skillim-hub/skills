#!/usr/bin/env python3
"""Scenario: invoice worker classification risk."""

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
    exclusive_service = env_bool("LABOR_LAW_ADVISOR_EXCLUSIVE_SERVICE", "true")
    invoices_multiple_clients = env_bool("LABOR_LAW_ADVISOR_INVOICES_MULTIPLE_CLIENTS")
    result = LaborLawAdvisor().classification_risk(
        integrated_in_business=env_bool("LABOR_LAW_ADVISOR_INTEGRATED_INTO_BUSINESS", "true"),
        fixed_schedule=not env_bool("LABOR_LAW_ADVISOR_SETS_OWN_SCHEDULE"),
        uses_company_tools=env_bool("LABOR_LAW_ADVISOR_USES_EMPLOYER_TOOLS", "true"),
        single_client=exclusive_service and not invoices_multiple_clients,
        can_send_substitute=env_bool("LABOR_LAW_ADVISOR_HIRES_SUBSTITUTES"),
        invoices_with_vat=invoices_multiple_clients,
    ).to_dict()
    result["environment"] = args.env
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
