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
    "expense_type": os.getenv("TAX_EXPENSE_TYPE", "home internet"),
    "business_purpose": os.getenv("TAX_BUSINESS_PURPOSE", "remote client work"),
    "has_invoice": os.getenv("TAX_HAS_INVOICE", "true").lower() == "true",
    "business_use_percent": float(os.getenv("TAX_BUSINESS_USE_PERCENT", "60")),
    "environment": args.env,
}
result = client.explain("expense-deductibility", facts=facts)
payload = result.to_dict()
payload["environment"] = args.env
print(json.dumps(payload, ensure_ascii=False, indent=2))
