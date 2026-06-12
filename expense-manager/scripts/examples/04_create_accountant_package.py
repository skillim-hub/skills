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
    rows = [
        ExpenseInput(date=date(2026, 3, 1), vendor="CPA", amount=parse_decimal("1170"), description="accountant", receipt_number="INV-CPA"),
        ExpenseInput(date=date(2026, 3, 2), vendor="KSP", amount=parse_decimal("5000"), description="laptop computer", receipt_number="INV-KSP"),
    ]
    results = classify_many(rows, config(args))
    output_dir = Path(args.output_dir)
    zip_path = export_accountant_package(results, output_dir, "demo-package")
    print(json.dumps({"env": args.env, "package_zip": str(zip_path), "summary": summarize_results(results)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
