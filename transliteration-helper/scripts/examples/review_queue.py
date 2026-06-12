#!/usr/bin/env python3
"""Manual-review queue example."""

from __future__ import annotations

import argparse
import json
import os

from transliteration_helper_client import TransliterationClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a review queue for ambiguous names.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("TRANSLITERATION_ENV", "sandbox"))
    parser.add_argument("--names", default=os.getenv("TRANSLITERATION_NAMES", "אבתיה|דוד Cohen|כהן|צבי"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    names = [name.strip() for name in args.names.split("|") if name.strip()]
    results = TransliterationClient().transliterate_many(names)
    payload = {
        "environment": args.env,
        "queue": [
            {
                "original": result.original,
                "latin": result.latin,
                "status": "review" if result.warnings else "approved",
                "warnings": list(result.warnings),
            }
            for result in results
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
