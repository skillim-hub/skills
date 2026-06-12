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
    statement = out_dir / "freelancer.csv"
    with statement.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerows([
            ["תאריך", "תיאור", "חובה", "זכות"],
            ["15/01/2026", "מע\"מ תקופתי", "1200", ""],
            ["16/01/2026", "העברה מלקוח חשבונית 1042", "", "5000"],
            ["17/01/2026", "בזק בינלאומי", "129", ""],
        ])
    result = BankTransactionCategorizer().categorize_file(statement, out_dir / "freelancer-categorized.json", "json")
    print(json.dumps({"environment": args.env, "summary": result["summary"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
