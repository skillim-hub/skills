#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os
from passport_id_scheduler_client import hebrew_checklist
parser = argparse.ArgumentParser(description="Print a Hebrew checklist for a minor ID card workflow.")
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PASSPORT_ID_SCHEDULER_ENV", "sandbox"))
args = parser.parse_args()
service = os.getenv("PASSPORT_ID_SERVICE", "id_first")
print(json.dumps({"environment": args.env, "service": service, "items": hebrew_checklist(service, minor=True)}, ensure_ascii=False, indent=2))
