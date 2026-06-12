"""Render SRT from a small transcript payload."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from hebrew_voice_to_text import HebrewVoiceTextClient, render_srt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("HVTT_ENV", "sandbox"))
    parser.add_argument("--output", default=os.getenv("HVTT_SRT_OUTPUT", "example.srt"))
    args = parser.parse_args()

    client = HebrewVoiceTextClient(env=args.env)
    result = client.parse_provider_payload({
        "language": "he-IL",
        "segments": [
            {"start": 0.0, "end": 2.0, "speaker": "לקוח", "text": "שלום, אפשר לקבל הצעת מחיר"},
            {"start": 2.0, "end": 4.0, "speaker": "עסק", "text": "כן, המחיר הוא ₪320"},
        ],
    })
    path = Path(args.output)
    path.write_text(render_srt(result), encoding="utf-8")
    print(json.dumps({"env": args.env, "written": str(path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
