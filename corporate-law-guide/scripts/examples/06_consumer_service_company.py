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
    activity = os.getenv("CLG_ACTIVITY", "consumer ecommerce and online services")
    owners = int(os.getenv("CLG_OWNERS", "1"))
    risk = os.getenv("CLG_LIABILITY_RISK", "high")
    fundraising = os.getenv("CLG_FUNDRAISING", "no").lower() in {"yes", "true", "1"}
    case = client.create_case(activity, owners)
    decision = client.classify_entity_need(activity, owners, risk, fundraising)
    print(json.dumps({"case": case.to_dict(), "decision": decision.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
