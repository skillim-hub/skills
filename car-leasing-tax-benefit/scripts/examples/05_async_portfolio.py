from __future__ import annotations

import argparse
import asyncio
import json
import os

from car_leasing_tax_benefit import CarLeasingTaxBenefitClient


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CAR_LEASING_TAX_BENEFIT_ENV", "sandbox"))
    return p


async def run(environment: str) -> None:
    client = CarLeasingTaxBenefitClient()
    tax_year = int(os.getenv("CAR_LEASING_TAX_BENEFIT_TAX_YEAR", "2026"))
    results = await client.calculate_many_async([
        {"original_price_ils": os.getenv("CAR_LEASING_TAX_BENEFIT_PRICE_A", "180000"), "category": "private_combustion", "tax_year": tax_year},
        {"original_price_ils": os.getenv("CAR_LEASING_TAX_BENEFIT_PRICE_B", "220000"), "category": "electric", "tax_year": tax_year},
    ])
    print(json.dumps({"environment": environment, "results": [item.to_dict() for item in results]}, ensure_ascii=False, indent=2))


args = parser().parse_args()
asyncio.run(run(args.env))
