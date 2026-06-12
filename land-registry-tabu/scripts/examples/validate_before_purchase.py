#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from land_registry_tabu import FileJsonTransport, LandRegistryTabuClient, ParcelId, TabuClientConfig, extract_risk_flags

ROOT = Path(__file__).resolve().parents[1]
ENV_URLS = {
    "sandbox": os.getenv("TABU_SANDBOX_BASE_URL", "https://sandbox.example.internal.gov-adapter.local"),
    "production": os.getenv("TABU_PRODUCTION_BASE_URL", "https://production.example.internal.gov-adapter.local"),
}

parser = argparse.ArgumentParser(description="Produce risk flags before purchase review.")
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("TABU_ENV", "sandbox"))
parser.add_argument("--base-url", default=None)
parser.add_argument("--api-key", default=os.getenv("TABU_API_KEY"))
parser.add_argument("--mock-file", default=str(ROOT / "fixtures" / "sample_parcel_response.json"))
args = parser.parse_args()

client = LandRegistryTabuClient(
    TabuClientConfig(base_url=args.base_url or ENV_URLS[args.env], api_key=args.api_key),
    transport=FileJsonTransport(args.mock_file),
)
extract = client.get_by_parcel(ParcelId(30001, 12, 4))
print(json.dumps({"risk_flags": extract_risk_flags(extract)}, ensure_ascii=False, indent=2))
