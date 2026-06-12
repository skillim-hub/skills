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
        "purpose": "quote",
        "formality": "formal",
        "environment": args.env,
        "recipient": {"name": env_value(args.env, "RECIPIENT_NAME", "מחלקת רכש"), "is_company": True},
        "sender": {"name": env_value(args.env, "SENDER_NAME", "נועה ברק"), "gender": env_value(args.env, "SENDER_GENDER", "female")},
        "facts": {
            "service": env_value(args.env, "SERVICE", "עיצוב עמוד נחיתה"),
            "amount": env_value(args.env, "AMOUNT", "4800"),
            "vat_status": env_value(args.env, "VAT_STATUS", "בתוספת מע\"מ כדין"),
            "valid_until": env_value(args.env, "VALID_UNTIL", "20/06/2026"),
            "timeline": env_value(args.env, "TIMELINE", "10 ימי עבודה"),
            "scope": ["אפיון קצר", "עיצוב מסך ראשי", "מסירה בקובץ Figma"]
        }
    }
    draft = HebrewEmailFormatterClient().compose(request)
    print(json.dumps(draft.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
