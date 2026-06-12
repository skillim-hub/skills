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

parser = argparse.ArgumentParser(description="Create an extract order, extract the order id, and read status.")
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("TABU_ENV", "sandbox"))
parser.add_argument("--base-url", default=None)
parser.add_argument("--api-key", default=os.getenv("TABU_API_KEY"))
parser.add_argument("--mock-file", default=str(ROOT / "fixtures" / "sample_parcel_response.json"))
parser.add_argument("--order-mock-file", default=str(ROOT / "fixtures" / "sample_order_response.json"))
args = parser.parse_args()

client = LandRegistryTabuClient(
    TabuClientConfig(base_url=args.base_url or ENV_URLS[args.env], api_key=args.api_key),
    transport=FileJsonTransport(args.mock_file, args.order_mock_file),
)
created = client.create_extract_order(ParcelId(30001, 12, 4), payment_reference=os.getenv("TABU_PAYMENT_REFERENCE", "PAY-SANDBOX-0001"))
order_id = created.order_id
status = client.get_order_status(order_id)
print(json.dumps({"created": created.to_dict(), "order_id": order_id, "status": status.to_dict()}, ensure_ascii=False, indent=2))
