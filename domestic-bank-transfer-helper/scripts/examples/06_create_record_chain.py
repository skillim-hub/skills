from __future__ import annotations

import argparse
import json
import os
from datetime import date

from domestic_bank_transfer_helper_client import TransferRequest, create_transfer_record, record_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a record, extract its id, and build a payload.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("DOMESTIC_TRANSFER_ENV", "sandbox"))
    parser.add_argument("--state-dir", default=os.getenv("DOMESTIC_TRANSFER_STATE_DIR", ".domestic-bank-transfer-helper"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    request = TransferRequest(
        recipient_name=os.getenv("DBTF_RECIPIENT_NAME", "Example Supplier Ltd"),
        bank_code=os.getenv("DBTF_BANK_CODE", "12"),
        branch_code=os.getenv("DBTF_BRANCH_CODE", "456"),
        account_number=os.getenv("DBTF_ACCOUNT_NUMBER", "123456789"),
        amount_ils=os.getenv("DBTF_AMOUNT_ILS", "2450.80"),
        value_date=os.getenv("DBTF_VALUE_DATE", "03/06/2026"),
        purpose=os.getenv("DBTF_PURPOSE", "Invoice 1007"),
        reference=os.getenv("DBTF_REFERENCE", "INV-1007"),
    )
    created = create_transfer_record(request, env=args.env, storage_dir=args.state_dir, today=date(2026, 6, 2))
    transfer_id = created["id"]
    payload = record_payload(transfer_id, env=args.env, storage_dir=args.state_dir)
    print(json.dumps({"created": created, "transfer_id": transfer_id, "payload": payload}, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
