from __future__ import annotations

import argparse
import asyncio
import json
import os

import httpx

import cbs_data_analyzer_client as cbs

SAMPLE_SERIES = {
    "month": [
        {
            "code": 120010,
            "name": "Consumer Price Index",
            "date": [{"year": 2026, "month": 4, "value": 106.4, "percent": 1.2, "percentYear": 1.9}],
        }
    ]
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run an asynchronous CBS price-index fetch.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CBS_ENV", "sandbox"))
    parser.add_argument("--index-id", type=int, default=int(os.getenv("CBS_EXAMPLE_INDEX_ID", "120010")))
    return parser.parse_args()


def sandbox_transport() -> httpx.MockTransport:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=SAMPLE_SERIES)

    return httpx.MockTransport(handler)


async def main_async() -> None:
    args = parse_args()
    kwargs: dict[str, object] = {}
    if args.env == "sandbox":
        kwargs["transport"] = sandbox_transport()
    else:
        kwargs["cbs_base_url"] = os.getenv("CBS_API_BASE_URL", cbs.CBS_INDEX_API_BASE)
        kwargs["data_gov_base_url"] = os.getenv("CBS_DATA_GOV_BASE_URL", cbs.DATA_GOV_API_BASE)

    async with cbs.AsyncCBSDataAnalyzerClient(**kwargs) as client:
        series = await client.get_price_index(args.index_id)
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
    asyncio.run(main_async())
