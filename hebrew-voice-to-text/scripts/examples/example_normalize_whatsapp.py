"""Normalize exported WhatsApp-style text."""

from __future__ import annotations

import argparse
import json
import os

from hebrew_voice_to_text import HebrewVoiceTextClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("HVTT_ENV", "sandbox"))
    parser.add_argument("--text", default=os.getenv("HVTT_SAMPLE_TEXT", "היי   שלחתי לך חשבונית על ₪450 ל-15/03/2026"))
    args = parser.parse_args()

    client = HebrewVoiceTextClient(env=args.env)
    payload = {
        "env": args.env,
        "normalized": client.normalize_hebrew_text(args.text),
        "sensitive_terms": client.detect_sensitive_terms(args.text),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
