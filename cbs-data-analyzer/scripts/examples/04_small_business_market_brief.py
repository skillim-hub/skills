from __future__ import annotations

import argparse
import json
import os

import cbs_data_analyzer_client as cbs

SAMPLE_SERIES = {
    "month": [
        {
            "code": 120010,
            "name": "Consumer Price Index",
            "date": [
                {"year": 2026, "month": 1, "value": 104.0},
                {"year": 2026, "month": 2, "value": 104.4},
                {"year": 2026, "month": 3, "value": 105.2},
                {"year": 2026, "month": 4, "value": 106.4},
            ],
        }
    ]
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a structured small-business market brief.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CBS_ENV", "sandbox"))
    parser.add_argument("--question", default=os.getenv("CBS_EXAMPLE_QUESTION", "Open a small cafe near a residential street"))
    parser.add_argument("--geography", default=os.getenv("CBS_EXAMPLE_GEOGRAPHY", "Haifa"))
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
        series = cbs.parse_price_series(SAMPLE_SERIES, index_id=120010, source_url="offline fixture")
    brief = cbs.build_market_brief(
        question=args.question,
        geography=args.geography,
        series=series,
        assumptions=[
            "Competition requires external field research",
            "CBS data may lag the current month",
        ],
    )
    print(json.dumps({"environment": args.env, "brief": brief}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
