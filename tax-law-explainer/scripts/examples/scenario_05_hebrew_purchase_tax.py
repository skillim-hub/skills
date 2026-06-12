from __future__ import annotations

import argparse
import json
import os

from tax_law_explainer import TaxLawExplainerClient

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("TAX_LAW_ENV", "sandbox"))
args = parser.parse_args()

client = TaxLawExplainerClient(default_language="he")
facts = {
    "asset_type": os.getenv("TAX_ASSET_TYPE_HE", "דירת מגורים"),
    "purchaser_status": os.getenv("TAX_PURCHASER_STATUS_HE", "תושב ישראל"),
    "owns_other_apartment": os.getenv("TAX_OWNS_OTHER_APARTMENT", "false").lower() == "true",
    "purchase_price": float(os.getenv("TAX_PURCHASE_PRICE", "2100000")),
    "environment": args.env,
}
result = client.explain("purchase-tax", facts=facts, language="he")
payload = result.to_dict()
payload["environment"] = args.env
print(json.dumps(payload, ensure_ascii=False, indent=2))
