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
        "purpose": "consumer_complaint",
        "formality": "formal",
        "environment": args.env,
        "recipient": {"name": env_value(args.env, "RECIPIENT_NAME", "שירות לקוחות"), "is_company": True},
        "sender": {"name": env_value(args.env, "SENDER_NAME", "רונית ישראלי"), "gender": env_value(args.env, "SENDER_GENDER", "female"), "phone": env_value(args.env, "SENDER_PHONE", "052-0000000")},
        "facts": {
            "product": env_value(args.env, "PRODUCT", "מכונת קפה"),
            "order_number": env_value(args.env, "ORDER_NUMBER", "A12345"),
            "purchase_date": env_value(args.env, "PURCHASE_DATE", "15/05/2026"),
            "amount": env_value(args.env, "AMOUNT", "899"),
            "problem": env_value(args.env, "PROBLEM", "המוצר הגיע תקול"),
            "requested_resolution": env_value(args.env, "RESOLUTION", "החלפה או החזר"),
            "requested_action_date": env_value(args.env, "ACTION_DATE", "10/06/2026")
        }
    }
    draft = HebrewEmailFormatterClient().compose(request)
    print(json.dumps(draft.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
