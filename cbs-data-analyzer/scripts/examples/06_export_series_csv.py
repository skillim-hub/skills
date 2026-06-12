from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

import cbs_data_analyzer_client as cbs

SAMPLE_SERIES = {
    "month": [
        {
            "code": 120010,
            "name": "Consumer Price Index",
            "date": [
                {"year": 2026, "month": 4, "value": 106.4},
                {"year": 2026, "month": 3, "value": 105.2},
            ],
        }
    ]
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a normalized price-index series to CSV.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CBS_ENV", "sandbox"))
    parser.add_argument("--output", default=os.getenv("CBS_EXAMPLE_OUTPUT", ""))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.env == "production":
        with cbs.CBSDataAnalyzerClient(
            cbs_base_url=os.getenv("CBS_API_BASE_URL", cbs.CBS_INDEX_API_BASE),
            data_gov_base_url=os.getenv("CBS_DATA_GOV_BASE_URL", cbs.DATA_GOV_API_BASE),
        ) as client:
            series = client.get_price_index(120010)
    else:
        series = cbs.parse_price_series(SAMPLE_SERIES, source_url="offline fixture")
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(args.output) if args.output else Path(tmp) / "cpi.csv"
        with cbs.CBSDataAnalyzerClient() as client:
            client.export_series_csv(series, target)
        payload = {
            "environment": args.env,
            "csv_path": str(target),
            "csv_text": target.read_text(encoding="utf-8"),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
