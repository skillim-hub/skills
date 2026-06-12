#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os
from pathlib import Path
from passport_id_scheduler_client import PassportIdSchedulerClient, parse_date, parse_time
parser = argparse.ArgumentParser(description="Create a local calendar file for an appointment.")
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PASSPORT_ID_SCHEDULER_ENV", "sandbox"))
args = parser.parse_args()
output = Path(os.getenv("PASSPORT_ID_ICS_PATH", "appointment.ics"))
written = PassportIdSchedulerClient().write_ics(output, os.getenv("PASSPORT_ID_EVENT_TITLE", "Passport renewal appointment"), parse_date(os.getenv("PASSPORT_ID_EVENT_DATE", "2026-08-15")), parse_time(os.getenv("PASSPORT_ID_EVENT_TIME", "09:30")), location=os.getenv("PASSPORT_ID_EVENT_LOCATION", "Population and Immigration Authority bureau"))
print(json.dumps({"environment": args.env, "written": str(written)}, ensure_ascii=False, indent=2))
