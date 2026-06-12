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

args = parser("Custom configuration override from environment variables.").parse_args()
config = TaxConfig.from_mapping({
    "vat_rate": os.getenv("FTC_VAT_RATE", "0.18"),
    "osek_patur_threshold_annual": os.getenv("FTC_OSEK_PATUR_THRESHOLD_ANNUAL", "122833"),
    "national_insurance_reduced_rate": os.getenv("FTC_NI_REDUCED_RATE", "0.077"),
    "national_insurance_regular_rate": os.getenv("FTC_NI_REGULAR_RATE", "0.18"),
})
calc = FreelancerTaxCalculator(config, environment=args.env)
report = calc.calculate(FreelancerTaxInput(
    business_type="osek-murshe",
    annual_revenue_ils=os.getenv("FTC_REVENUE_ILS", "180000"),
    deductible_expenses_ils=os.getenv("FTC_EXPENSES_ILS", "45000"),
    input_vat_ils=os.getenv("FTC_INPUT_VAT_ILS", "3600"),
    income_tax_advance_rate=os.getenv("FTC_ADVANCE_RATE", "0.07"),
))
print_json({"config": config, "report": report})
