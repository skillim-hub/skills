from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path

from expense_manager import (
    BusinessConfig,
    EntityType,
    ExpenseInput,
    async_classify_many,
    classify_csv_file,
    classify_expense,
    classify_many,
    create_expense_record,
    export_accountant_package,
    parse_decimal,
    summarize_results,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("EXPENSE_MANAGER_ENV", "sandbox"))
    parser.add_argument("--output-dir", default=os.getenv("EXPENSE_MANAGER_OUTPUT_DIR", "./out"))
    return parser.parse_args()


def config(args: argparse.Namespace) -> BusinessConfig:
    return BusinessConfig(
        entity_type=EntityType(os.getenv("EXPENSE_MANAGER_ENTITY_TYPE", "osek_murshe")),
        home_office_percent=parse_decimal(os.getenv("EXPENSE_MANAGER_HOME_OFFICE_PERCENT", "0")),
        strict=args.env == "production",
    )


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    input_csv = output_dir / "input.csv"
    output_csv = output_dir / "classified.csv"
    input_csv.write_text("date,vendor,amount,description\n15/01/2026,Bezeq,117,internet\n", encoding="utf-8")
    results = classify_csv_file(input_csv, output_csv, config(args))
    print(json.dumps({"env": args.env, "output_csv": str(output_csv), "summary": summarize_results(results)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
