#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

from land_registry_tabu import FileJsonTransport, LandRegistryTabuClient, ParcelId, TabuClientConfig

ROOT = Path(__file__).resolve().parents[1]
ENV_URLS = {
    "sandbox": os.getenv("TABU_SANDBOX_BASE_URL", "https://sandbox.example.internal.gov-adapter.local"),
    "production": os.getenv("TABU_PRODUCTION_BASE_URL", "https://production.example.internal.gov-adapter.local"),
}

parser = argparse.ArgumentParser(description="Export right-holder rows to CSV or JSON.")
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("TABU_ENV", "sandbox"))
parser.add_argument("--base-url", default=None)
parser.add_argument("--api-key", default=os.getenv("TABU_API_KEY"))
parser.add_argument("--mock-file", default=str(ROOT / "fixtures" / "sample_parcel_response.json"))
parser.add_argument("--format", choices=["csv", "json"], default="csv")
args = parser.parse_args()

client = LandRegistryTabuClient(
    TabuClientConfig(base_url=args.base_url or ENV_URLS[args.env], api_key=args.api_key),
    transport=FileJsonTransport(args.mock_file),
)
extract = client.get_by_parcel(ParcelId(30001, 12, 4))
rows = [right.to_dict() for right in extract.rights]
if args.format == "json":
    print(json.dumps(rows, ensure_ascii=False, indent=2))
else:
    writer = csv.DictWriter(sys.stdout, fieldnames=["owner_name", "id_masked", "right_type", "share", "deed_date", "deed_number", "encumbrances"])
    writer.writeheader()
    writer.writerows(rows)
