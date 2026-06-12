from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from bank_transaction_categorizer import BankTransactionCategorizer, RawTransaction, parse_israeli_date


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("BTC_ENV", "sandbox"))
    parser.add_argument("--output-dir", default=os.getenv("BTC_OUTPUT_DIR", str(Path(__file__).with_suffix("").parent / "_out")))
    return parser

from decimal import Decimal

def main() -> None:
    args = build_parser().parse_args()
    transactions = [
        RawTransaction(parse_israeli_date("10/01/2026"), "ADOBE CREATIVE CLOUD", Decimal("-88")),
        RawTransaction(parse_israeli_date("12/01/2026"), "זיכוי ADOBE CREATIVE CLOUD", Decimal("88")),
    ]
    rows = BankTransactionCategorizer().categorize_transactions(transactions)
    print(json.dumps({
        "environment": args.env,
        "note": "Keep both rows and review the net effect.",
        "transactions": [row.to_dict() for row in rows],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
