#!/usr/bin/env python3
"""Import appointment rows from CSV and preview confirmations."""
from __future__ import annotations

import argparse
import csv
import json
import os
from io import StringIO

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
    csv_data = """customer_name,customer_phone,service_name,start_at,duration_minutes,price_ils,location
דנה,054-123-4567,ייעוץ ראשוני,2026-06-18T10:30:00+03:00,45,250,"רחוב הרצל 10, תל אביב"
יואב,052-111-2222,תספורת,2026-06-18T15:00:00+03:00,30,90,"דיזנגוף 50, תל אביב"
"""
    client = make_client(args.env)
    previews = []
    for row in csv.DictReader(StringIO(csv_data)):
        appointment = client.create_appointment(row["customer_name"], row["customer_phone"], row["service_name"], row["start_at"], int(row["duration_minutes"]), os.getenv("BOT_BUSINESS_NAME", "העסק לדוגמה"), price_ils=float(row["price_ils"]), location=row["location"])
        previews.append({"appointment_id": appointment.appointment_id, "text": client.build_confirmation_text(appointment)})
    print(json.dumps(previews, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
