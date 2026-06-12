from __future__ import annotations

import argparse
import json
import os

from hebrew_email_formatter import HebrewEmailFormatterClient


def env_value(env_name: str, key: str, default: str) -> str:
    scoped = os.environ.get(f"HEF_{env_name.upper()}_{key}")
    generic = os.environ.get(f"HEF_{key}")
    return scoped or generic or default


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
    args = parser.parse_args()

    request = {
        "purpose": "payment_reminder",
        "environment": args.env,
        "recipient": {"name": env_value(args.env, "RECIPIENT_NAME", "דנה"), "gender": env_value(args.env, "RECIPIENT_GENDER", "female")},
        "sender": {"name": env_value(args.env, "SENDER_NAME", "יואב לוי"), "gender": env_value(args.env, "SENDER_GENDER", "male"), "email": env_value(args.env, "SENDER_EMAIL", "yoav@example.co.il")},
        "facts": {
            "invoice_number": env_value(args.env, "INVOICE_NUMBER", "2026-041"),
            "invoice_date": env_value(args.env, "INVOICE_DATE", "01/05/2026"),
            "due_date": env_value(args.env, "DUE_DATE", "31/05/2026"),
            "amount": env_value(args.env, "AMOUNT", "3500"),
            "payment_terms": env_value(args.env, "PAYMENT_TERMS", "שוטף + 30")
        }
    }
    draft = HebrewEmailFormatterClient().compose(request)
    print(json.dumps(draft.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
