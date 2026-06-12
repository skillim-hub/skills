#!/usr/bin/env python3
"""CSV batch example."""

from __future__ import annotations

import argparse
import csv
import json
import os
import tempfile
from pathlib import Path

from transliteration_helper_client import TransliterationClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transliterate a CSV customer-name column.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("TRANSLITERATION_ENV", "sandbox"))
    parser.add_argument("--input-csv", type=Path, default=os.getenv("TRANSLITERATION_INPUT_CSV"))
    parser.add_argument("--input-column", default=os.getenv("TRANSLITERATION_INPUT_COLUMN", "hebrew_name"))
    return parser.parse_args()


def sample_csv(path: Path) -> None:
    path.write_text("hebrew_name,customer_id\nדוד כהן,1001\nשרה לוי,1002\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    client = TransliterationClient()
    with tempfile.TemporaryDirectory() as tmp:
        input_path = args.input_csv or Path(tmp) / "customers.csv"
        if args.input_csv is None:
            sample_csv(input_path)
        output_path = Path(tmp) / "customers_latin.csv"
        results = client.transliterate_file(input_path, input_column=args.input_column, output_path=output_path, output_format="csv")
        rows = list(csv.DictReader(output_path.open(encoding="utf-8")))
        payload = {
            "environment": args.env,
            "input": str(input_path),
            "output_rows": rows,
            "review_count": sum(1 for result in results if result.warnings),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
