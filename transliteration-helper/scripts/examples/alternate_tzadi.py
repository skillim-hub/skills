#!/usr/bin/env python3
"""Alternate tzadi-rendering example."""

from __future__ import annotations

import argparse
import json
import os

from transliteration_helper_client import TransliterationClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare alternate צ/ץ renderings.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("TRANSLITERATION_ENV", "sandbox"))
    parser.add_argument("--name", default=os.getenv("TRANSLITERATION_NAME", "צבי"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = TransliterationClient()
    payload = {
        "environment": args.env,
        "name": args.name,
        "variants": {
            style: client.transliterate(args.name, strict=True, tzadi_style=style).to_dict()
            for style in ["z", "tz", "ts"]
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
