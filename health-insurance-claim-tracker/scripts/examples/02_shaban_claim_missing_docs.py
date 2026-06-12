from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from health_insurance_claim_tracker import HealthInsuranceClaimTrackerClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.environ.get("HICT_ENV", "sandbox"))
    parser.add_argument("--storage", default=os.environ.get("HICT_STORAGE_PATH"))
    return parser.parse_args()


def build_client(args: argparse.Namespace) -> HealthInsuranceClaimTrackerClient:
    if args.storage:
        storage = Path(args.storage)
    else:
        storage = Path(tempfile.gettempdir()) / f"hict-example-{args.env}.json"
    return HealthInsuranceClaimTrackerClient(storage)


def emit(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main() -> None:
    args = parse_args()
    client = build_client(args)
    claim = client.create_claim(
        claimant_reference=os.environ.get("HICT_CLAIMANT_REF", "member-2244"),
        policy_type=os.environ.get("HICT_POLICY_TYPE", "supplementary"),
        provider=os.environ.get("HICT_PROVIDER", "Kupat Holim Supplementary Plan"),
        service_date=os.environ.get("HICT_SERVICE_DATE", "02/03/2026"),
        submission_date=os.environ.get("HICT_SUBMISSION_DATE", "12/03/2026"),
        amount_claimed_ils=os.environ.get("HICT_AMOUNT", "320.00"),
        description=os.environ.get("HICT_DESCRIPTION", "Supplementary plan physiotherapy reimbursement"),
        channel=os.environ.get("HICT_CHANNEL", "clinic branch"),
        service_kind=os.environ.get("HICT_SERVICE_KIND", "physiotherapy"),
    )
    claim = client.add_document(claim.id, name="receipt.pdf", document_type="tax_invoice_or_receipt")
    emit({"env": args.env, "id": claim.id, "missing_documents": claim.missing_documents()})


if __name__ == "__main__":
    main()
