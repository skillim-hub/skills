#!/usr/bin/env python3
"""Preview and optionally send an appointment confirmation."""
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
    appointment = client.create_appointment(
        "דנה", "054-123-4567", "ייעוץ ראשוני", "2026-06-18T10:30:00+03:00", 45,
        os.getenv("BOT_BUSINESS_NAME", "קליניקת הדוגמה"), price_ils=250, location="רחוב הרצל 10, תל אביב"
    )
    result = client.send_appointment_confirmation(appointment, dry_run=not args.send)
    print(json.dumps({"appointment_id": appointment.appointment_id, "text": client.build_confirmation_text(appointment), "result": result.raw}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
