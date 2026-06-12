from __future__ import annotations

import argparse
import json
import os
from datetime import date

from domestic_bank_transfer_helper_client import TransferRequest, build_bank_form_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a same-day Zahav payload.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("DOMESTIC_TRANSFER_ENV", "sandbox"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    request = TransferRequest(
        recipient_name=os.getenv("DBTF_RECIPIENT_NAME", "Critical Supplier Ltd"),
        bank_code=os.getenv("DBTF_BANK_CODE", "12"),
        branch_code=os.getenv("DBTF_BRANCH_CODE", "456"),
        account_number=os.getenv("DBTF_ACCOUNT_NUMBER", "123456789"),
        amount_ils=os.getenv("DBTF_AMOUNT_ILS", "18500"),
        value_date=os.getenv("DBTF_VALUE_DATE", "03/06/2026"),
        purpose=os.getenv("DBTF_PURPOSE", "Urgent machine repair"),
        reference=os.getenv("DBTF_REFERENCE", "REPAIR-77"),
        same_day=True,
        approved_by=os.getenv("DBTF_APPROVED_BY", "Finance Manager"),
    )
    payload = build_bank_form_payload(request, env=args.env, today=date(2026, 6, 2))
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
