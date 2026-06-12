#!/usr/bin/env python3
"""Find nearest shelters from an environment-configured CSV/JSON/GeoJSON file."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from red_alert_shelter_finder import RedAlertShelterFinderClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
    parser.add_argument("--lat", type=float, default=float(os.getenv("RED_ALERT_LAT", "32.074")))
    parser.add_argument("--lon", type=float, default=float(os.getenv("RED_ALERT_LON", "34.779")))
    parser.add_argument("--limit", type=int, default=int(os.getenv("RED_ALERT_LIMIT", "3")))
    args = parser.parse_args()

    shelters_file = os.getenv("RED_ALERT_SHELTERS_FILE")
    client = RedAlertShelterFinderClient()
    if shelters_file:
        shelters = client.load_shelters_file(shelters_file)
    else:
        csv_text = """name,address,city,latitude,longitude
מקלט ציבורי 12,הרצל 10,תל אביב - יפו,32.073,34.780
מקלט ציבורי 13,דיזנגוף 50,תל אביב - יפו,32.077,34.774
"""
        shelters = client.load_shelters_text(csv_text, format_hint="csv", source="inline")
    nearest = [shelter.to_dict() for shelter in client.nearest_shelters(args.lat, args.lon, shelters, limit=args.limit)]
    print(json.dumps({"environment": args.env, "nearest": nearest}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
