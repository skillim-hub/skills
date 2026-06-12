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
    owners = int(os.getenv("CLG_OWNERS", "2"))
    activity = os.getenv("CLG_ACTIVITY", "B2B software platform")
    regulated = os.getenv("CLG_REGULATED", "no").lower() in {"yes", "true", "1"}
    foreign = os.getenv("CLG_FOREIGN_SHAREHOLDERS", "no").lower() in {"yes", "true", "1"}
    case = client.create_case(activity, owners)
    result = client.build_incorporation_checklist(
        owners_count=owners,
        business_activity=activity,
        regulated_activity=regulated,
        foreign_shareholders=foreign,
        case_id=case.case_id,
    )
    print(json.dumps({"case": case.to_dict(), "checklist": result.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
