from __future__ import annotations

import argparse
import json
import os

import httpx

import cbs_data_analyzer_client as cbs

SAMPLE_SERIES = {
    "month": [
        {
            "code": 120010,
            "name": "Consumer Price Index",
            "date": [
                {"year": 2026, "month": 4, "currBase": {"value": 106.4}, "percent": 1.2, "percentYear": 1.9},
                {"year": 2026, "month": 3, "currBase": {"value": 105.2}, "percent": -0.1, "percentYear": 1.7},
            ],
        }
    ]
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch or simulate the latest CPI point.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CBS_ENV", "sandbox"))
    parser.add_argument("--index-id", type=int, default=int(os.getenv("CBS_EXAMPLE_INDEX_ID", "120010")))
    return parser.parse_args()


def sandbox_client() -> cbs.CBSDataAnalyzerClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=SAMPLE_SERIES)

    return cbs.CBSDataAnalyzerClient(transport=httpx.MockTransport(handler))


def production_client() -> cbs.CBSDataAnalyzerClient:
    return cbs.CBSDataAnalyzerClient(
        cbs_base_url=os.getenv("CBS_API_BASE_URL", cbs.CBS_INDEX_API_BASE),
        data_gov_base_url=os.getenv("CBS_DATA_GOV_BASE_URL", cbs.DATA_GOV_API_BASE),
    )


def main() -> None:
    args = parse_args()
    factory = sandbox_client if args.env == "sandbox" else production_client
    with factory() as client:
        series = client.get_price_index(args.index_id)
    latest = series.latest
    payload = {
        "environment": args.env,
        "series": series.name,
        "code": series.code,
        "latest": latest.to_dict() if latest else None,
        "source": series.source_url,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
