#!/usr/bin/env python3
"""Create action steps for a customer-facing business."""

from __future__ import annotations

import argparse
import json
import os

from red_alert_shelter_finder import RedAlertShelterFinderClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
    parser.add_argument("--city", default=os.getenv("RED_ALERT_BUSINESS_CITY", "אשדוד"))
    parser.add_argument("--business-type", default=os.getenv("RED_ALERT_BUSINESS_TYPE", "restaurant"))
    args = parser.parse_args()

    client = RedAlertShelterFinderClient()
    procedure = {
        "environment": args.env,
        "city": args.city,
        "business_type": args.business_type,
        "active_alert_steps": client.action_steps(active=True, outside=False, business=True),
        "ready_state_steps": client.action_steps(active=False, business=True),
    }
    print(json.dumps(procedure, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
