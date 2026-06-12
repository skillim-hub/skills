from __future__ import annotations

import argparse
import csv
import json
import os
from datetime import date
from tempfile import NamedTemporaryFile

from domestic_bank_transfer_helper_client import load_transfers_csv, validate_transfers


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a small payroll MASAV batch.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("DOMESTIC_TRANSFER_ENV", "sandbox"))
    parser.add_argument("--csv-path", default=os.getenv("DBTF_PAYROLL_CSV", ""))
    return parser.parse_args()


def create_demo_csv() -> str:
    handle = NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False, suffix=".csv")
    with handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["recipient_name", "bank_code", "branch_code", "account_number", "amount_ils", "value_date", "purpose", "bulk_count"],
        )
        writer.writeheader()
        writer.writerow({"recipient_name": "Employee One", "bank_code": "12", "branch_code": "456", "account_number": "123456789", "amount_ils": "9700", "value_date": "09/06/2026", "purpose": "Salary 05/2026", "bulk_count": "2"})
        writer.writerow({"recipient_name": "Employee Two", "bank_code": "10", "branch_code": "800", "account_number": "987654321", "amount_ils": "8800", "value_date": "09/06/2026", "purpose": "Salary 05/2026", "bulk_count": "2"})
    return handle.name


def main() -> None:
    args = parse_args()
    csv_path = args.csv_path or create_demo_csv()
    reports = validate_transfers(load_transfers_csv(csv_path), env=args.env, today=date(2026, 6, 2))
    print(json.dumps({"reports": [report.to_dict() for report in reports]}, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
