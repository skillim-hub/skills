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
        claimant_reference=os.environ.get("HICT_CLAIMANT_REF", "case-9900"),
        policy_type=os.environ.get("HICT_POLICY_TYPE", "private"),
        provider=os.environ.get("HICT_PROVIDER", "Example Insurance"),
        service_date=os.environ.get("HICT_SERVICE_DATE", "10/02/2026"),
        submission_date=os.environ.get("HICT_SUBMISSION_DATE", "18/02/2026"),
        amount_claimed_ils=os.environ.get("HICT_AMOUNT", "4000.00"),
        description=os.environ.get("HICT_DESCRIPTION", "Procedure reimbursement with partial approval"),
        channel=os.environ.get("HICT_CHANNEL", "email"),
        service_kind=os.environ.get("HICT_SERVICE_KIND", "surgery"),
    )
    claim = client.add_reimbursement(claim.id, amount_ils=os.environ.get("HICT_REIMBURSEMENT_AMOUNT", "1500.00"), paid_date=os.environ.get("HICT_PAID_DATE", "20/03/2026"), payer=os.environ.get("HICT_PAYER", "Example Insurance"))
    claim = client.update_claim_status(claim.id, "appealed", note="Attach medical necessity letter and policy clause reference.")
    emit({"env": args.env, "claim": claim.to_dict(redact=True)})


if __name__ == "__main__":
    main()
