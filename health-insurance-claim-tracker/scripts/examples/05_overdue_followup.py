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
        claimant_reference=os.environ.get("HICT_CLAIMANT_REF", "household-3311"),
        policy_type=os.environ.get("HICT_POLICY_TYPE", "supplementary"),
        provider=os.environ.get("HICT_PROVIDER", "Kupat Holim Supplementary Plan"),
        service_date=os.environ.get("HICT_SERVICE_DATE", "10/01/2026"),
        submission_date=os.environ.get("HICT_SUBMISSION_DATE", "15/01/2026"),
        amount_claimed_ils=os.environ.get("HICT_AMOUNT", "180.00"),
        description=os.environ.get("HICT_DESCRIPTION", "Old supplementary claim requiring follow-up"),
        channel=os.environ.get("HICT_CHANNEL", "branch"),
        follow_up_date=os.environ.get("HICT_FOLLOW_UP_DATE", "15/02/2026"),
    )
    emit({"env": args.env, "created": claim.id, "overdue": [item.to_dict(redact=True) for item in client.overdue_claims(as_of=os.environ.get("HICT_AS_OF_DATE", "01/03/2026"))]})


if __name__ == "__main__":
    main()
