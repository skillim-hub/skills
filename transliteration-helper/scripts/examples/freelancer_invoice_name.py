#!/usr/bin/env python3
"""Freelancer invoice-name example."""

from __future__ import annotations

import argparse
import json
import os

from transliteration_helper_client import TransliterationClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare Latin customer name for an invoice draft.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("TRANSLITERATION_ENV", "sandbox"))
    parser.add_argument("--customer", default=os.getenv("TRANSLITERATION_CUSTOMER_NAME", "שרה לוי"))
    parser.add_argument("--amount", default=os.getenv("TRANSLITERATION_INVOICE_AMOUNT", "₪1,250"))
    parser.add_argument("--issue-date", default=os.getenv("TRANSLITERATION_ISSUE_DATE", "03/06/2026"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = TransliterationClient().transliterate(args.customer, output_case="title")
    payload = {
        "environment": args.env,
        "invoice": {
            "customer_original": result.original,
            "customer_latin": result.latin,
            "amount": args.amount,
            "issue_date": args.issue_date,
            "review_required": bool(result.warnings),
            "warnings": list(result.warnings),
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
