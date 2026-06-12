#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os
from passport_id_scheduler_client import AppointmentPreference, AppointmentRequest, PassportIdSchedulerClient, parse_date
parser = argparse.ArgumentParser(description="Build a passport renewal plan.")
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PASSPORT_ID_SCHEDULER_ENV", "sandbox"))
args = parser.parse_args()
request = AppointmentRequest(service=os.getenv("PASSPORT_ID_SERVICE", "passport_renewal"), preference=AppointmentPreference(preferred_city=os.getenv("PASSPORT_ID_CITY", "Tel Aviv-Yafo"), date_from=parse_date(os.getenv("PASSPORT_ID_DATE_FROM", "2026-08-01")), date_to=parse_date(os.getenv("PASSPORT_ID_DATE_TO", "2026-08-31"))))
plan = PassportIdSchedulerClient().build_plan(request)
print(json.dumps({"environment": args.env, "plan": plan.to_dict()}, ensure_ascii=False, indent=2))
