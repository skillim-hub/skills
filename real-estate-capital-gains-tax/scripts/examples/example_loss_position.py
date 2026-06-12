from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from real_estate_capital_gains_tax import TaxInputs, estimate_tax


def build_inputs(env: str) -> TaxInputs:
    tax_rate = float(os.getenv("MAS_SHEVACH_TAX_RATE", "0.25"))
    purchase_price = float(os.getenv("MAS_SHEVACH_PURCHASE_PRICE", "2300000"))
    sale_price = float(os.getenv("MAS_SHEVACH_SALE_PRICE", "2180000"))
    payload = {
        "purchase_date": os.getenv("MAS_SHEVACH_PURCHASE_DATE", "2021-01-01"),
        "sale_date": os.getenv("MAS_SHEVACH_SALE_DATE", "2025-01-01"),
        "purchase_price": purchase_price,
        "sale_price": sale_price,
        "purchase_costs": float(os.getenv("MAS_SHEVACH_PURCHASE_COSTS", "0")),
        "sale_costs": float(os.getenv("MAS_SHEVACH_SALE_COSTS", "0")),
        "improvements": float(os.getenv("MAS_SHEVACH_IMPROVEMENTS", "0")),
        "depreciation_claimed": float(os.getenv("MAS_SHEVACH_DEPRECIATION", "0")),
        "ownership_share": float(os.getenv("MAS_SHEVACH_OWNERSHIP_SHARE", "1")),
        "property_type": os.getenv("MAS_SHEVACH_PROPERTY_TYPE", "residential_apartment"),
        "is_qualifying_residential_apartment": os.getenv("MAS_SHEVACH_QUALIFYING_RESIDENTIAL", "false").lower() in {"1", "true", "yes"},
        "seller_residency": os.getenv("MAS_SHEVACH_SELLER_RESIDENCY", "unknown"),
        "seller_type": os.getenv("MAS_SHEVACH_SELLER_TYPE", "individual"),
        "tax_rate": tax_rate,
        "exemption_code": os.getenv("MAS_SHEVACH_EXEMPTION_CODE", None),
        "notes": os.getenv("MAS_SHEVACH_NOTES", ""),
    }
    cpi_purchase = os.getenv("MAS_SHEVACH_CPI_PURCHASE", "")
    cpi_sale = os.getenv("MAS_SHEVACH_CPI_SALE", "")
    if cpi_purchase and cpi_sale:
        payload["cpi_purchase"] = float(cpi_purchase)
        payload["cpi_sale"] = float(cpi_sale)
    payload["environment"] = env
    payload.pop("environment")
    return TaxInputs.from_dict(payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("MAS_SHEVACH_ENV", "sandbox"))
    args = parser.parse_args()
    estimate = estimate_tax(build_inputs(args.env))
    print(json.dumps(estimate.rounded(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
