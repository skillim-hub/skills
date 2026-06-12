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
    seller_shares = int(os.getenv("CLG_SELLER_SHARES", "5000"))
    quantity = int(os.getenv("CLG_TRANSFER_QUANTITY", "1000"))
    family = os.getenv("CLG_FAMILY_TRANSFER", "yes").lower() in {"yes", "true", "1"}
    new_holder = os.getenv("CLG_NEW_SHAREHOLDER", "yes").lower() in {"yes", "true", "1"}
    tax_done = os.getenv("CLG_TAX_REVIEW_DONE", "no").lower() in {"yes", "true", "1"}
    case = client.create_case(os.getenv("CLG_ACTIVITY", "share transfer"), 2)
    result = client.share_transfer_checklist(seller_shares, quantity, family, new_holder, tax_done, case_id=case.case_id)
    print(json.dumps({"case": case.to_dict(), "share_transfer": result.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
