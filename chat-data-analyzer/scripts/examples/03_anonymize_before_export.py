from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from chat_data_analyzer_client import anonymize_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mask identifiers before sharing examples.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CHAT_ANALYZER_ENV", "sandbox"))
    parser.add_argument("--text", default=os.getenv("CHAT_ANALYZER_TEXT", "המייל שלי dana@example.co.il, הטלפון 052-765-4321 ותז 123456782"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = {"env": args.env, "masked_text": anonymize_text(args.text)}
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
