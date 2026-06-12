#!/usr/bin/env python3
"""Create a watch, extract its id, and use it in the next check step."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from red_alert_shelter_finder import RedAlertShelterFinderClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
    parser.add_argument("--area", default=os.getenv("RED_ALERT_AREA", "חיפה"))
    args = parser.parse_args()

    payload_file = os.getenv("RED_ALERT_SANDBOX_ALERTS_FILE" if args.env == "sandbox" else "RED_ALERT_PRODUCTION_ALERTS_FILE")
    payload = Path(payload_file).read_text(encoding="utf-8") if payload_file else '{"id":"watch-demo","data":["חיפה"]}'

    client = RedAlertShelterFinderClient()
    create_response = client.create_watch(args.area, environment=args.env).to_dict()
    watch_id = create_response["watch_id"]
    watch = client.create_watch(args.area, environment=args.env)
    alerts = client.parse_alert_payload(payload)
    check_response = client.check_watch(watch, alerts)

    print(json.dumps({"create_response": create_response, "watch_id_used": watch_id, "check_response": check_response}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
