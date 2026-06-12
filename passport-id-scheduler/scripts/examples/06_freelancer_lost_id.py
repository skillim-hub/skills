#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os
from passport_id_scheduler_client import AppointmentRequest, PassportIdSchedulerClient
parser = argparse.ArgumentParser(description="Plan a lost ID workflow for a self-employed person.")
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PASSPORT_ID_SCHEDULER_ENV", "sandbox"))
args = parser.parse_args()
request = AppointmentRequest(service=os.getenv("PASSPORT_ID_SERVICE", "id_lost_stolen"), business_context=os.getenv("PASSPORT_ID_BUSINESS_CONTEXT", "self_employed"))
plan = PassportIdSchedulerClient().build_plan(request)
print(json.dumps({"environment": args.env, "plan": plan.to_dict()}, ensure_ascii=False, indent=2))
