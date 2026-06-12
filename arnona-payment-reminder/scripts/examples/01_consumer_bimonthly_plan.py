from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from arnona_payment_reminder import ArnonaBill, ArnonaPaymentReminderClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env",
        choices=["sandbox", "production"],
        default=os.getenv("ARNONA_PAYMENT_REMINDER_ENV", "sandbox"),
    )
    parser.add_argument("--as-of", default=os.getenv("ARNONA_AS_OF"))
    parser.add_argument("--output-dir", default=os.getenv("ARNONA_OUTPUT_DIR", "."))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = ArnonaPaymentReminderClient.with_default_profiles()
    bill = ArnonaBill.from_dict({
        "municipality": os.getenv("ARNONA_MUNICIPALITY", "Holon"),
        "account_reference": os.getenv("ARNONA_ACCOUNT_REFERENCE", "421337800"),
        "bill_number": os.getenv("ARNONA_BILL_NUMBER", "2026-02-44127"),
        "taxpayer_name": os.getenv("ARNONA_TAXPAYER_NAME", "Dana Levi"),
        "property_address": os.getenv("ARNONA_PROPERTY_ADDRESS", "Sokolov 12/7, Holon"),
        "period_start": os.getenv("ARNONA_PERIOD_START", "2026-01-01"),
        "period_end": os.getenv("ARNONA_PERIOD_END", "2026-02-28"),
        "issue_date": os.getenv("ARNONA_ISSUE_DATE", "2026-01-05"),
        "due_date": os.getenv("ARNONA_DUE_DATE", "2026-02-28"),
        "amount_nis": os.getenv("ARNONA_AMOUNT_NIS", "782.40"),
        "status": "unpaid",
    })
    plan = client.build_reminder_plan(bill, as_of=args.as_of or "2026-02-01", language="en")
    print(json.dumps({"environment": args.env, "plan": plan.to_dict()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
