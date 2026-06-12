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
    "activity_type": os.getenv("TAX_ACTIVITY_TYPE", "design"),
    "profession": os.getenv("TAX_PROFESSION", "graphic designer"),
    "annual_turnover": float(os.getenv("TAX_ANNUAL_TURNOVER", "120000")),
    "start_date": os.getenv("TAX_START_DATE", "02/06/2026"),
    "environment": args.env,
}
result = client.explain("vat-registration", user_type=os.getenv("TAX_USER_TYPE", "freelancer"), facts=facts)
payload = result.to_dict()
payload["environment"] = args.env
print(json.dumps(payload, ensure_ascii=False, indent=2))
