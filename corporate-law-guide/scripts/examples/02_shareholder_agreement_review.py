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
    founders = int(os.getenv("CLG_FOUNDERS", "2"))
    equal = os.getenv("CLG_EQUAL_HOLDINGS", "yes").lower() in {"yes", "true", "1"}
    investor = os.getenv("CLG_INVESTOR_ROUND", "yes").lower() in {"yes", "true", "1"}
    family = os.getenv("CLG_FAMILY_COMPANY", "no").lower() in {"yes", "true", "1"}
    case = client.create_case(os.getenv("CLG_ACTIVITY", "founder venture"), founders)
    result = client.shareholder_agreement_scan(founders, equal, investor, family, case_id=case.case_id)
    print(json.dumps({"case": case.to_dict(), "scan": result.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
