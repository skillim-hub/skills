#!/usr/bin/env python3
"""Parse an incoming WhatsApp webhook payload."""
from __future__ import annotations

import argparse
import json
import os

from whatsapp_scheduling_bot import WhatsAppSchedulingClient


def make_client(env: str) -> WhatsAppSchedulingClient:
    prefix = "WHATSAPP" if env == "production" else "WHATSAPP_SANDBOX"
    return WhatsAppSchedulingClient(
        access_token=os.getenv(f"{prefix}_ACCESS_TOKEN", os.getenv("WHATSAPP_ACCESS_TOKEN", "dry")),
        phone_number_id=os.getenv(f"{prefix}_PHONE_ID", os.getenv("WHATSAPP_PHONE_ID", "dry")),
        api_version=os.getenv("WHATSAPP_API_VERSION", "v25.0"),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
    args = parser.parse_args()
    payload = {"entry": [{"changes": [{"value": {"contacts": [{"wa_id": "972541234567", "profile": {"name": "דנה"}}], "messages": [{"from": "972541234567", "id": "wamid.example", "timestamp": "1718700000", "type": "text", "text": {"body": "אפשר תור למחר בבוקר?"}}]}}]}]}
    client = make_client(args.env)
    events = client.parse_webhook_payload(payload)
    print(json.dumps([{**event.__dict__, "classification": client.classify_reply(event.text)} for event in events], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
