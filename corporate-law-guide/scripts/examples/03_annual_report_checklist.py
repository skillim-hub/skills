#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os

from corporate_law_guide import CorporateLawGuideClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CLG_ENV", "sandbox"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = CorporateLawGuideClient(environment=args.env)
    company_number = os.getenv("CLG_COMPANY_NUMBER", "516000000")
    year = int(os.getenv("CLG_REPORT_YEAR", "2026"))
    changes = os.getenv("CLG_HAS_CHANGES", "yes").lower() in {"yes", "true", "1"}
    case = client.create_case(os.getenv("CLG_ACTIVITY", "active company"), 1, company_number=company_number)
    result = client.annual_report_checklist(company_number, year, changes, case_id=case.case_id)
    print(json.dumps({"case": case.to_dict(), "annual_report": result.to_dict(), "regulatory_facts": client.regulatory_facts_payload()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
