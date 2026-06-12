from __future__ import annotations

import argparse
import json
import os

import httpx

import cbs_data_analyzer_client as cbs

CATALOG = {
    "chapters": [
        {"mainCode": 120010, "chapterName": "Consumer Price Index - General"},
        {"mainCode": 40010, "chapterName": "מדד מחירי דירות"},
        {"mainCode": 170030, "chapterName": "Producer prices"},
    ]
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Search the CBS price-index catalog.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CBS_ENV", "sandbox"))
    parser.add_argument("--query", default=os.getenv("CBS_EXAMPLE_QUERY", "דירות"))
    return parser.parse_args()


def sandbox_client() -> cbs.CBSDataAnalyzerClient:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=CATALOG)

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
        matches = client.search_catalog(args.query)
    print(json.dumps({"environment": args.env, "query": args.query, "matches": matches}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
