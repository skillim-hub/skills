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
tax_year = int(os.getenv("CAR_LEASING_TAX_BENEFIT_TAX_YEAR", "2026"))
price = Decimal(os.getenv("CAR_LEASING_TAX_BENEFIT_ORIGINAL_PRICE_ILS", "180000"))
tax_rate = Decimal(os.getenv("CAR_LEASING_TAX_BENEFIT_MARGINAL_TAX_RATE", "0.35"))
result = client.calculate(VehicleInput(original_price_ils=price, category="private_combustion", tax_year=tax_year, employee_marginal_tax_rate=tax_rate))
print(json.dumps({"environment": args.env, "result": result.to_dict()}, ensure_ascii=False, indent=2))
