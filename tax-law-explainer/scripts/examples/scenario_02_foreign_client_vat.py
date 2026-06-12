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
    "client_residence": os.getenv("TAX_CLIENT_RESIDENCE", "Germany"),
    "beneficiary": os.getenv("TAX_BENEFICIARY", "foreign parent company"),
    "use_location": os.getenv("TAX_USE_LOCATION", "outside Israel"),
    "contract": os.getenv("TAX_CONTRACT", "signed consulting agreement"),
    "environment": args.env,
}
result = client.explain("foreign-client-vat", facts=facts)
payload = result.to_dict()
payload["environment"] = args.env
print(json.dumps(payload, ensure_ascii=False, indent=2))
