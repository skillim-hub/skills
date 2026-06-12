"""Scan and redact sensitive transcript values."""

from __future__ import annotations

import argparse
import json
import os

from hebrew_voice_to_text import HebrewVoiceTextClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("HVTT_ENV", "sandbox"))
    parser.add_argument("--text", default=os.getenv("HVTT_PRIVACY_TEXT", "הטלפון שלי 052-1234567 ותעודת זהות 123456789"))
    args = parser.parse_args()

    client = HebrewVoiceTextClient(env=args.env)
    payload = {
        "env": args.env,
        "terms": client.detect_sensitive_terms(args.text),
        "redacted": client.redact_sensitive_text(args.text),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
