#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os
from dataclasses import asdict
from passport_id_scheduler_client import ApplicantProfile
parser = argparse.ArgumentParser(description="Validate an applicant profile locally.")
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PASSPORT_ID_SCHEDULER_ENV", "sandbox"))
args = parser.parse_args()
profile = ApplicantProfile(os.getenv("PASSPORT_ID_FULL_NAME", "Example Applicant"), os.getenv("PASSPORT_ID_TZ", "123456782"), os.getenv("PASSPORT_ID_PHONE", "+972 52 123 4567"), os.getenv("PASSPORT_ID_EMAIL", "person@example.co.il"))
print(json.dumps({"environment": args.env, "profile": asdict(profile.normalized())}, ensure_ascii=False, indent=2))
