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
        "municipality": os.getenv("ARNONA_MUNICIPALITY", "Haifa"),
        "account_reference": os.getenv("ARNONA_ACCOUNT_REFERENCE", "445566778"),
        "bill_number": os.getenv("ARNONA_BILL_NUMBER", "HF-2026-333"),
        "taxpayer_name": os.getenv("ARNONA_TAXPAYER_NAME", "North Office"),
        "property_address": os.getenv("ARNONA_PROPERTY_ADDRESS", "HaNamal 8, Haifa"),
        "period_start": os.getenv("ARNONA_PERIOD_START", "2026-01-01"),
        "period_end": os.getenv("ARNONA_PERIOD_END", "2026-02-28"),
        "issue_date": os.getenv("ARNONA_ISSUE_DATE", "2026-01-05"),
        "due_date": os.getenv("ARNONA_DUE_DATE", "2026-02-28"),
        "amount_nis": os.getenv("ARNONA_AMOUNT_NIS", "2210.00"),
        "status": "unpaid",
    })
    plan = client.build_reminder_plan(bill, as_of=args.as_of or "2026-03-12", language="en")
    response = {
        "environment": args.env,
        "current_balance_check_required": plan.status == "overdue",
        "plan": plan.to_dict(),
    }
    print(json.dumps(response, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
