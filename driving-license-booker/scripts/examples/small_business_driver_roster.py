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
    names = os.getenv("DLB_DRIVER_NAMES", "דנה לוי,משה כהן").split(",")
    ids = os.getenv("DLB_DRIVER_IDS", "039456785,123456782").split(",")
    phones = os.getenv("DLB_DRIVER_PHONES", "0501234567,0527654321").split(",")
    applicants = [Applicant(name.strip(), national_id.strip(), phone.strip(), license_number=None) for name, national_id, phone in zip(names, ids, phones)]
    emit({"drivers": client.export_roster(applicants), "environment": args.env})


if __name__ == "__main__":
    main()
