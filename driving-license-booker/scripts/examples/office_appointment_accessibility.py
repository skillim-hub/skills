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
        os.getenv("DLB_FULL_NAME", "משה כהן"),
        os.getenv("DLB_NATIONAL_ID", "123456782"),
        os.getenv("DLB_PHONE", "0527654321"),
        license_number=os.getenv("DLB_LICENSE_NUMBER", "7654321"),
    )
    window = TimeWindow(dt.date.fromisoformat(os.getenv("DLB_APPOINTMENT_DATE", "2026-07-15")), city=os.getenv("DLB_CITY", "חיפה"))
    payload = client.build_bureau_appointment_payload(applicant, [window], service_city=os.getenv("DLB_CITY", "חיפה"), accessibility_needed=True)
    emit(client.create_booking({"kind": "bureau_appointment", **payload}))


if __name__ == "__main__":
    main()
