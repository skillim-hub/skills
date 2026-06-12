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
        "purpose": "meeting_request",
        "formality": "warm",
        "environment": args.env,
        "recipient": {"name": env_value(args.env, "RECIPIENT_NAME", "מאיה"), "gender": env_value(args.env, "RECIPIENT_GENDER", "female")},
        "sender": {"name": env_value(args.env, "SENDER_NAME", "רוני"), "gender": env_value(args.env, "SENDER_GENDER", "neutral")},
        "facts": {
            "topic": env_value(args.env, "TOPIC", "תכנון רבעוני"),
            "duration": env_value(args.env, "DURATION", "30 דקות"),
            "medium": env_value(args.env, "MEDIUM", "שיחת וידאו"),
            "slots": ["יום א, 07/06/2026, בשעה 10:00", "יום ב, 08/06/2026, בשעה 12:30", "יום ג, 09/06/2026, בשעה 15:00"]
        }
    }
    draft = HebrewEmailFormatterClient().compose(request)
    print(json.dumps(draft.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
