#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import os

from freelancer_tax_calculator import FreelancerTaxCalculator, FreelancerTaxInput, decimal_to_json, load_environment_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Async batch scenario estimate.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("FTC_ENV", "sandbox"))
    return parser


async def main() -> None:
    args = build_parser().parse_args()
    calc = FreelancerTaxCalculator(load_environment_config(args.env), environment=args.env)
    scenarios = [
        FreelancerTaxInput("osek-patur", os.getenv("FTC_PATUR_REVENUE_ILS", "95000"), income_tax_advance_rate="0.06"),
        FreelancerTaxInput("osek-murshe", os.getenv("FTC_MURSHE_REVENUE_ILS", "240000"), "65000", "5100", "0.08"),
    ]
    reports = await calc.calculate_many_async(scenarios)
    print(json.dumps(decimal_to_json(reports), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
