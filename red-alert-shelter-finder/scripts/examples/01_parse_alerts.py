#!/usr/bin/env python3
"""Parse alerts from an environment-configured payload file or sandbox sample."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from red_alert_shelter_finder import RedAlertShelterFinderClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
    args = parser.parse_args()

    payload_file = os.getenv("RED_ALERT_SANDBOX_ALERTS_FILE" if args.env == "sandbox" else "RED_ALERT_PRODUCTION_ALERTS_FILE")
    payload = Path(payload_file).read_text(encoding="utf-8") if payload_file else '{"id":"demo","title":"ירי רקטות וטילים","data":["חיפה","קריית אתא"]}'
    client = RedAlertShelterFinderClient()
    alerts = [alert.to_dict() for alert in client.parse_alert_payload(payload)]
    print(json.dumps({"environment": args.env, "alerts": alerts}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
