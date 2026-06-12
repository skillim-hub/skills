from __future__ import annotations

import argparse
import json
import os
from datetime import date

from domestic_bank_transfer_helper_client import TransferRequest, format_report, validate_transfer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print a Hebrew validation report.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("DOMESTIC_TRANSFER_ENV", "sandbox"))
    parser.add_argument("--json-output", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    request = TransferRequest(
        recipient_name=os.getenv("DBTF_RECIPIENT_NAME", "ספק לדוגמה בעמ"),
        bank_code=os.getenv("DBTF_BANK_CODE", "12"),
        branch_code=os.getenv("DBTF_BRANCH_CODE", "45"),
        account_number=os.getenv("DBTF_ACCOUNT_NUMBER", "123456789"),
        amount_ils=os.getenv("DBTF_AMOUNT_ILS", "12000"),
        value_date=os.getenv("DBTF_VALUE_DATE", "03/06/2026"),
        purpose=os.getenv("DBTF_PURPOSE", "חשבונית 1007"),
    )
    report = validate_transfer(request, env=args.env, today=date(2026, 6, 2))
    if args.json_output:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2, default=str))
    else:
        print(format_report(report, language="he"))


if __name__ == "__main__":
    main()
