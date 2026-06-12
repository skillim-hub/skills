from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from bank_transaction_categorizer import BankTransactionCategorizer, create_sample_statement


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("BTC_ENV", "sandbox"))
    parser.add_argument("--output-dir", default=os.getenv("BTC_OUTPUT_DIR", str(Path(__file__).with_suffix("").parent / "_out")))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    create_response = create_sample_statement(out_dir / "sample.csv", environment=args.env, base_dir=out_dir / "state")
    result = BankTransactionCategorizer().categorize_file(create_response["path"], out_dir / "categorized.csv")
    print(json.dumps({"environment": args.env, "create": create_response, "summary": result["summary"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
