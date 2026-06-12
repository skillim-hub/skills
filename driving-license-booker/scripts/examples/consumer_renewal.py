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
    applicant = Applicant(
        os.getenv("DLB_FULL_NAME", "דנה לוי"),
        os.getenv("DLB_NATIONAL_ID", "039456785"),
        os.getenv("DLB_PHONE", "0501234567"),
        license_number=os.getenv("DLB_LICENSE_NUMBER", "1234567"),
    )
    payload = client.build_renewal_payload(applicant, expiry_date=os.getenv("DLB_EXPIRY_DATE", "2026-08-31"))
    emit(client.create_booking({"kind": "license_renewal", **payload}))


if __name__ == "__main__":
    main()
