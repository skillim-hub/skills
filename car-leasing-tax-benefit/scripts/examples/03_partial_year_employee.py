from __future__ import annotations

import argparse
import json
import os
from decimal import Decimal

from car_leasing_tax_benefit import CarLeasingTaxBenefitClient, VehicleInput


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CAR_LEASING_TAX_BENEFIT_ENV", "sandbox"))
    return p

args = parser().parse_args()
client = CarLeasingTaxBenefitClient()
payload = {
    "original_price_ils": os.getenv("CAR_LEASING_TAX_BENEFIT_ORIGINAL_PRICE_ILS", "165000"),
    "category": os.getenv("CAR_LEASING_TAX_BENEFIT_CATEGORY", "hybrid"),
    "tax_year": int(os.getenv("CAR_LEASING_TAX_BENEFIT_TAX_YEAR", "2026")),
    "months_available": int(os.getenv("CAR_LEASING_TAX_BENEFIT_MONTHS_AVAILABLE", "5")),
    "employee_marginal_tax_rate": os.getenv("CAR_LEASING_TAX_BENEFIT_MARGINAL_TAX_RATE", "0.31"),
    "employee_name": os.getenv("CAR_LEASING_TAX_BENEFIT_EMPLOYEE_NAME", "Dana"),
    "license_plate": os.getenv("CAR_LEASING_TAX_BENEFIT_LICENSE_PLATE", "123-45-678"),
}
result = client.calculate(payload)
print(json.dumps({"environment": args.env, "result": result.to_dict()}, ensure_ascii=False, indent=2))
