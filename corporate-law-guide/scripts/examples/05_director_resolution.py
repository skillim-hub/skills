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
    action = os.getenv("CLG_DIRECTOR_ACTION", "appoint")
    bank_change = os.getenv("CLG_BANK_SIGNING_CHANGE", "yes").lower() in {"yes", "true", "1"}
    case = client.create_case(os.getenv("CLG_ACTIVITY", "director update"), 1)
    result = client.director_change_checklist(action, bank_change, case_id=case.case_id)
    print(json.dumps({"case": case.to_dict(), "director_change": result.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
