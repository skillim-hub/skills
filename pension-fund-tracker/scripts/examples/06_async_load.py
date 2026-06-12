#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path

from pension_fund_tracker import AsyncPensionFundTrackerClient, records_to_dicts


def sample_file() -> Path:
    path = Path(os.getenv("PENSION_TRACKER_SAMPLE_PATH", "/tmp/pension_tracker_sample.csv"))
    path.write_text("fund_id,fund_name,report_date\n1,Fund,2025-12-31\n", encoding="utf-8")
    return path


async def main() -> None:
    parser = argparse.ArgumentParser(description="Load a local CSV using the async client")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PENSION_TRACKER_ENV", "sandbox"))
    parser.add_argument("--input", default=os.getenv("PENSION_TRACKER_INPUT", ""))
    args = parser.parse_args()
    path = Path(args.input) if args.input else sample_file()
    records = await AsyncPensionFundTrackerClient().load_csv(path, encoding="utf-8")
    print(json.dumps({"env": args.env, "records": records_to_dicts(records)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
