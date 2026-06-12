#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os

from freelancer_tax_calculator import FreelancerTaxCalculator, FreelancerTaxInput, TaxConfig, decimal_to_json, load_environment_config


def parser(description: str) -> argparse.ArgumentParser:
    arg_parser = argparse.ArgumentParser(description=description)
    arg_parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("FTC_ENV", "sandbox"))
    return arg_parser


def print_json(payload) -> None:
    print(json.dumps(decimal_to_json(payload), ensure_ascii=False, indent=2))

args = parser("Osek murshe VAT period estimate.").parse_args()
calc = FreelancerTaxCalculator(load_environment_config(args.env), environment=args.env)
report = calc.calculate(FreelancerTaxInput(
    business_type="osek-murshe",
    annual_revenue_ils=os.getenv("FTC_PERIOD_REVENUE_ILS", "50000"),
    input_vat_ils=os.getenv("FTC_PERIOD_INPUT_VAT_ILS", "2400"),
))
print_json({"environment": args.env, "vat": report.vat, "warnings": report.warnings})
