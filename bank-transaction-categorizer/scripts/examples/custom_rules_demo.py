from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from bank_transaction_categorizer import BankTransactionCategorizer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("BTC_ENV", "sandbox"))
    parser.add_argument("--output-dir", default=os.getenv("BTC_OUTPUT_DIR", str(Path(__file__).with_suffix("").parent / "_out")))
    return parser

import csv

def main() -> None:
    args = build_parser().parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rules = out_dir / "rules.json"
    rules.write_text(json.dumps([{
        "id": "coworking_space",
        "category": "Rent & Facilities",
        "subcategory": "Coworking",
        "patterns": ["חלל עבודה מרכזי"],
        "direction": "debit",
        "vat_relevant": True,
        "tax_deductibility": "likely",
        "confidence": 0.96,
        "priority": 250
    }], ensure_ascii=False, indent=2), encoding="utf-8")

    statement = out_dir / "custom.csv"
    with statement.open("w", encoding="utf-8-sig", newline="") as fh:
        csv.writer(fh).writerows([
            ["תאריך", "תיאור", "חובה", "זכות"],
            ["05/01/2026", "חלל עבודה מרכזי", "1500", ""],
        ])

    cat = BankTransactionCategorizer.from_rule_file(rules)
    result = cat.categorize_file(statement)
    print(json.dumps({"environment": args.env, "summary": result["summary"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
