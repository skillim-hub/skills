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

args = parser("Annual osek murshe summary as JSON.").parse_args()
calc = FreelancerTaxCalculator(load_environment_config(args.env), environment=args.env)
report = calc.calculate(FreelancerTaxInput(
    business_type=os.getenv("FTC_BUSINESS_TYPE", "osek-murshe"),
    annual_revenue_ils=os.getenv("FTC_REVENUE_ILS", "300000"),
    deductible_expenses_ils=os.getenv("FTC_EXPENSES_ILS", "80000"),
    input_vat_ils=os.getenv("FTC_INPUT_VAT_ILS", "7200"),
    income_tax_advance_rate=os.getenv("FTC_ADVANCE_RATE", "0.10"),
    income_tax_advance_base=os.getenv("FTC_ADVANCE_BASE", "revenue"),
))
print_json(report)
