#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from land_registry_tabu import FileJsonTransport, LandRegistryTabuClient, ParcelId, TabuClientConfig

ROOT = Path(__file__).resolve().parents[1]
ENV_URLS = {
    "sandbox": os.getenv("TABU_SANDBOX_BASE_URL", "https://sandbox.example.internal.gov-adapter.local"),
    "production": os.getenv("TABU_PRODUCTION_BASE_URL", "https://production.example.internal.gov-adapter.local"),
}


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("TABU_ENV", "sandbox"))
    parser.add_argument("--base-url", default=None)
    parser.add_argument("--api-key", default=os.getenv("TABU_API_KEY"))
    parser.add_argument("--mock-file", default=str(ROOT / "fixtures" / "sample_parcel_response.json"))
    return parser


def build_client(args: argparse.Namespace) -> LandRegistryTabuClient:
    base_url = args.base_url or ENV_URLS[args.env]
    return LandRegistryTabuClient(
        TabuClientConfig(base_url=base_url, api_key=args.api_key),
        transport=FileJsonTransport(args.mock_file),
    )

parser = build_parser("Fetch a parcel and print normalized JSON.")
parser.add_argument("--block", type=int, default=30001)
parser.add_argument("--parcel", type=int, default=12)
parser.add_argument("--subparcel", type=int, default=4)
args = parser.parse_args()

client = build_client(args)
extract = client.get_by_parcel(ParcelId(args.block, args.parcel, args.subparcel))
print(json.dumps(extract.to_dict(), ensure_ascii=False, indent=2))
