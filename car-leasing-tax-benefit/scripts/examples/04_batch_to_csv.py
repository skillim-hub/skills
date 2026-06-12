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

from pathlib import Path

args = parser().parse_args()
client = CarLeasingTaxBenefitClient()
tax_year = int(os.getenv("CAR_LEASING_TAX_BENEFIT_TAX_YEAR", "2026"))
vehicles = [
    {"employee_name": os.getenv("CAR_LEASING_TAX_BENEFIT_EMPLOYEE_1", "Noa"), "original_price_ils": "155000", "category": "private_combustion", "tax_year": tax_year, "employee_marginal_tax_rate": "0.31"},
    {"employee_name": os.getenv("CAR_LEASING_TAX_BENEFIT_EMPLOYEE_2", "Avi"), "original_price_ils": "205000", "category": "plugin_hybrid", "tax_year": tax_year, "employee_marginal_tax_rate": "0.35"},
    {"employee_name": os.getenv("CAR_LEASING_TAX_BENEFIT_EMPLOYEE_3", "Maya"), "original_price_ils": "240000", "category": "electric", "tax_year": tax_year, "employee_marginal_tax_rate": "0.47"},
]
results = client.calculate_many(vehicles)
path = Path(os.getenv("CAR_LEASING_TAX_BENEFIT_OUTPUT_CSV", str(Path(__file__).resolve().with_name("batch_output.csv"))))
client.export_csv(results, path)
print(json.dumps({"environment": args.env, "output_csv": str(path), "results": [item.to_dict() for item in results]}, ensure_ascii=False, indent=2))
