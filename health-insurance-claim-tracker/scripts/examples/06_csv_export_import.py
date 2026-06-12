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
        claimant_reference=os.environ.get("HICT_CLAIMANT_REF", "csv-5566"),
        policy_type=os.environ.get("HICT_POLICY_TYPE", "private"),
        provider=os.environ.get("HICT_PROVIDER", "Example Insurance"),
        service_date=os.environ.get("HICT_SERVICE_DATE", "01/02/2026"),
        submission_date=os.environ.get("HICT_SUBMISSION_DATE", "09/02/2026"),
        amount_claimed_ils=os.environ.get("HICT_AMOUNT", "990.00"),
        description=os.environ.get("HICT_DESCRIPTION", "CSV export/import scenario"),
        channel=os.environ.get("HICT_CHANNEL", "portal"),
    )
    output = Path(os.environ.get("HICT_CSV_PATH", str(Path(tempfile.gettempdir()) / "hict-export.csv")))
    client.export_csv(output)
    imported = HealthInsuranceClaimTrackerClient(Path(tempfile.gettempdir()) / f"hict-import-{args.env}.json").import_csv(output)
    emit({"env": args.env, "exported_path": str(output), "created": claim.id, "imported_count": len(imported)})


if __name__ == "__main__":
    main()
