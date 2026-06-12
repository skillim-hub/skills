from __future__ import annotations

import argparse
import datetime as dt
import json
import os

from driving_license_booker import Applicant, DrivingLicenseBookerClient, TimeWindow


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("DLB_ENV", "sandbox"))
    p.add_argument("--state", default=os.getenv("DLB_STATE", ".example-state.json"))
    return p


def emit(payload):
    if hasattr(payload, "to_dict"):
        payload = payload.to_dict()
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def main() -> None:
    args = parser().parse_args()
    client = DrivingLicenseBookerClient(environment=args.env, state_path=args.state)
    expiry = dt.date.fromisoformat(os.getenv("DLB_EXPIRY_DATE", "2026-08-31"))
    applicant = Applicant(
        os.getenv("DLB_FULL_NAME", "אורי עצמאי"),
        os.getenv("DLB_NATIONAL_ID", "039456785"),
        os.getenv("DLB_PHONE", "0501234567"),
        license_number=os.getenv("DLB_LICENSE_NUMBER", "9988776"),
    )
    readiness = client.check_renewal_readiness(applicant=applicant, expiry_date=expiry, has_paid_fee=os.getenv("DLB_HAS_PAID", "false").lower() == "true")
    readiness["business_day_follow_up"] = client.business_day_deadline(dt.date.today(), 7).isoformat()
    emit(readiness)


if __name__ == "__main__":
    main()
