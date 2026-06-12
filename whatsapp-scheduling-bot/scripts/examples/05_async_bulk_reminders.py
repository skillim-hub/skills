#!/usr/bin/env python3
"""Async dry-run reminder dispatch."""
from __future__ import annotations

import argparse
import asyncio
import json
import os

from whatsapp_scheduling_bot import AsyncWhatsAppSchedulingClient, WhatsAppSchedulingClient


def make_client(env: str) -> WhatsAppSchedulingClient:
    prefix = "WHATSAPP" if env == "production" else "WHATSAPP_SANDBOX"
    return WhatsAppSchedulingClient(
        access_token=os.getenv(f"{prefix}_ACCESS_TOKEN", os.getenv("WHATSAPP_ACCESS_TOKEN", "dry")),
        phone_number_id=os.getenv(f"{prefix}_PHONE_ID", os.getenv("WHATSAPP_PHONE_ID", "dry")),
        api_version=os.getenv("WHATSAPP_API_VERSION", "v25.0"),
    )


async def run(env: str, send: bool) -> None:
    sync_client = make_client(env)
    appointment = sync_client.create_appointment("מיכל", "058-765-4321", "אימון אישי", "2026-06-18T08:00:00+03:00", 60, os.getenv("BOT_BUSINESS_NAME", "סטודיו הדוגמה"), price_ils=180, location="הנמל 3, חיפה")
    async_client = AsyncWhatsAppSchedulingClient(sync_client)
    results = await async_client.send_due_reminders("2026-06-17T08:01:00+03:00", dry_run=not send)
    print(json.dumps({"appointment_id": appointment.appointment_id, "results": [r.raw for r in results]}, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
    parser.add_argument("--send", action="store_true")
    args = parser.parse_args()
    asyncio.run(run(args.env, args.send))


if __name__ == "__main__":
    main()
