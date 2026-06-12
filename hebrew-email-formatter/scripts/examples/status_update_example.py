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
        "purpose": "status_update",
        "formality": "neutral",
        "environment": args.env,
        "recipient": {"name": env_value(args.env, "RECIPIENT_NAME", "אלון"), "gender": env_value(args.env, "RECIPIENT_GENDER", "male")},
        "sender": {"name": env_value(args.env, "SENDER_NAME", "נועה"), "gender": env_value(args.env, "SENDER_GENDER", "female")},
        "facts": {
            "project": env_value(args.env, "PROJECT", "אתר החברה"),
            "completed": ["אפיון עמוד הבית", "בחירת כיוון עיצובי"],
            "next": ["עיצוב עמוד שירותים", "הכנת גרסה למובייל"],
            "attention": ["נדרש אישור לטקסט הפתיחה עד 12/06/2026"]
        }
    }
    draft = HebrewEmailFormatterClient().compose(request)
    print(json.dumps(draft.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
