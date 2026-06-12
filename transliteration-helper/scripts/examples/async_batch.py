#!/usr/bin/env python3
"""Asynchronous batch example."""

from __future__ import annotations

import argparse
import asyncio
import json
import os

from transliteration_helper_client import TransliterationClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run asynchronous batch transliteration.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("TRANSLITERATION_ENV", "sandbox"))
    parser.add_argument("--names", default=os.getenv("TRANSLITERATION_NAMES", "דוד|שרה|משה|לוי"))
    return parser.parse_args()


async def run(names: list[str]) -> list[dict[str, object]]:
    client = TransliterationClient()
    results = await client.transliterate_many_async(names)
    return [result.to_dict() for result in results]


def main() -> None:
    args = parse_args()
    names = [name.strip() for name in args.names.split("|") if name.strip()]
    payload = {"environment": args.env, "results": asyncio.run(run(names))}
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
