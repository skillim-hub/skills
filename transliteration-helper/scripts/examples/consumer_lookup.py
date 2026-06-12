#!/usr/bin/env python3
"""Consumer-facing lookup example."""

from __future__ import annotations

import argparse
import json
import os

from transliteration_helper_client import TransliterationClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transliterate one consumer name.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("TRANSLITERATION_ENV", "sandbox"))
    parser.add_argument("--name", default=os.getenv("TRANSLITERATION_NAME", "דוד כהן"))
    parser.add_argument("--case", choices=["upper", "title", "lower", "preserve"], default=os.getenv("TRANSLITERATION_OUTPUT_CASE", "title"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = TransliterationClient().transliterate(args.name, output_case=args.case, explain=args.env == "sandbox")
    payload = {"environment": args.env, "result": result.to_dict()}
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
