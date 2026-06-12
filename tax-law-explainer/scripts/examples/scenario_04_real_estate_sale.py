from __future__ import annotations

import argparse
import json
import os

from tax_law_explainer import TaxLawExplainerClient

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("TAX_LAW_ENV", "sandbox"))
args = parser.parse_args()

client = TaxLawExplainerClient(default_language=os.getenv("TAX_LAW_LANGUAGE", "en"))
facts = {
    "asset_type": os.getenv("TAX_ASSET_TYPE", "residential_apartment"),
    "purchase_date": os.getenv("TAX_PURCHASE_DATE", "15/06/2018"),
    "sale_date": os.getenv("TAX_SALE_DATE", "20/07/2026"),
    "purchase_price": float(os.getenv("TAX_PURCHASE_PRICE", "1600000")),
    "sale_price": float(os.getenv("TAX_SALE_PRICE", "2400000")),
    "family_unit_holdings": os.getenv("TAX_FAMILY_UNIT_HOLDINGS", "one apartment"),
    "construction_rights": os.getenv("TAX_CONSTRUCTION_RIGHTS", "false").lower() == "true",
    "environment": args.env,
}
result = client.explain("real-estate-sale", facts=facts)
payload = result.to_dict()
payload["environment"] = args.env
print(json.dumps(payload, ensure_ascii=False, indent=2))
