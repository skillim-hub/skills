#!/usr/bin/env python3
"""Load shelters from GeoJSON and print normalized records."""

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

    geojson_file = os.getenv("RED_ALERT_GEOJSON_FILE")
    if geojson_file:
        geojson = json.loads(Path(geojson_file).read_text(encoding="utf-8"))
    else:
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [34.780, 32.073]},
                    "properties": {"name": "מקלט ציבורי 12", "address": "הרצל 10", "city": "תל אביב - יפו"},
                }
            ],
        }

    client = RedAlertShelterFinderClient()
    shelters = [shelter.to_dict() for shelter in client.load_shelters_payload(geojson, source="geojson")]
    print(json.dumps({"environment": args.env, "shelters": shelters}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
