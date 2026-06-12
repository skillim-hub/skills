#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os
from datetime import date, time
from passport_id_scheduler_client import AppointmentCandidate, AppointmentPreference, AppointmentRequest, PassportIdSchedulerClient
parser = argparse.ArgumentParser(description="Rank user-provided official appointment slots.")
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PASSPORT_ID_SCHEDULER_ENV", "sandbox"))
args = parser.parse_args()
request = AppointmentRequest(service=os.getenv("PASSPORT_ID_SERVICE", "passport_renewal"), preference=AppointmentPreference(preferred_city=os.getenv("PASSPORT_ID_CITY", "Haifa")))
slots = [AppointmentCandidate("Bureau A", "Haifa", date(2026, 8, 10), time(9, 0), service="passport_renewal", source_url="https://govisit.gov.il/"), AppointmentCandidate("Bureau B", "Krayot", date(2026, 8, 5), time(11, 0), service="passport_renewal", source_url="https://govisit.gov.il/")]
ranked = PassportIdSchedulerClient().rank_candidates(request, slots)
print(json.dumps({"environment": args.env, "ranked": [slot.to_dict() for slot in ranked]}, ensure_ascii=False, indent=2))
