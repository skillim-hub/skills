#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os

from pension_fund_tracker import PensionFundTrackerClient, records_to_dicts

parser = argparse.ArgumentParser(description="Fetch a CKAN resource when a resource id is supplied")
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PENSION_TRACKER_ENV", "sandbox"))
parser.add_argument("--resource-id", default=os.getenv("PENSION_TRACKER_RESOURCE_ID", ""))
parser.add_argument("--max-records", type=int, default=int(os.getenv("PENSION_TRACKER_MAX_RECORDS", "10")))
args = parser.parse_args()

if args.env == "sandbox" or not args.resource_id:
    output = {"env": args.env, "skipped": True, "reason": "Set PENSION_TRACKER_RESOURCE_ID and --env production to fetch public CKAN data."}
else:
    records = PensionFundTrackerClient().fetch_ckan(args.resource_id, max_records=args.max_records)
    output = {"env": args.env, "records": records_to_dicts(records)}
print(json.dumps(output, ensure_ascii=False, indent=2))
