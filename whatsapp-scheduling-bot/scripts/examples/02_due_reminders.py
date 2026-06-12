#!/usr/bin/env python3
"""Send due reminders in dry-run mode unless --send is supplied."""
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
    parser.add_argument("--send", action="store_true")
    args = parser.parse_args()
    client = make_client(args.env)
    appointment = client.create_appointment("יואב", "+972 52 111 2222", "תספורת", "2026-06-18T15:00:00+03:00", 30, os.getenv("BOT_BUSINESS_NAME", "ברבריית הדוגמה"), price_ils=90, location="דיזנגוף 50, תל אביב")
    results = client.send_due_reminders("2026-06-17T15:01:00+03:00", dry_run=not args.send)
    print(json.dumps({"appointment_id": appointment.appointment_id, "results": [r.raw for r in results]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
