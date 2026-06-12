#!/usr/bin/env python3
"""Fetch alerts asynchronously using a sandbox or file-backed transport."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from red_alert_shelter_finder import RedAlertShelterFinderClient


async def main_async() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
    args = parser.parse_args()

    payload_file = os.getenv("RED_ALERT_SANDBOX_ALERTS_FILE" if args.env == "sandbox" else "RED_ALERT_PRODUCTION_ALERTS_FILE")
    payload = Path(payload_file).read_text(encoding="utf-8") if payload_file else '{"id":"async-demo","data":["רמת גן"]}'

    async def transport(url: str, timeout: float, headers: dict[str, str]) -> str:
        await asyncio.sleep(0.01)
        return payload

    client = RedAlertShelterFinderClient(async_transport=transport)
    alerts = [alert.to_dict() for alert in await client.fetch_current_alerts_async()]
    print(json.dumps({"environment": args.env, "alerts": alerts}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main_async())
