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
        claimant_reference=os.environ.get("HICT_CLAIMANT_REF", "business-owner-1020"),
        policy_type=os.environ.get("HICT_POLICY_TYPE", "private"),
        provider=os.environ.get("HICT_PROVIDER", "Example Insurance"),
        service_date=os.environ.get("HICT_SERVICE_DATE", "04/04/2026"),
        submission_date=os.environ.get("HICT_SUBMISSION_DATE", "06/04/2026"),
        amount_claimed_ils=os.environ.get("HICT_AMOUNT", "600.00"),
        description=os.environ.get("HICT_DESCRIPTION", "Self-employed medical expense pending reimbursement"),
        channel=os.environ.get("HICT_CHANNEL", "portal"),
        service_kind=os.environ.get("HICT_SERVICE_KIND", "consultation"),
        tags=["bookkeeping", "self-employed"],
    )
    client.add_reimbursement(claim.id, amount_ils=os.environ.get("HICT_REIMBURSEMENT_AMOUNT", "250.00"), paid_date=os.environ.get("HICT_PAID_DATE", "30/04/2026"), payer=os.environ.get("HICT_PAYER", "Example Insurance"))
    emit({"env": args.env, "summary": client.summary(), "gap_ils": str(client.reimbursement_gap(claim.id))})


if __name__ == "__main__":
    main()
