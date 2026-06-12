from __future__ import annotations

import argparse
import json
import os

from tax_return_filing_assistant_client import FilingProfile, TaxReturnAssistantClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("TAX_ASSISTANT_ENV", "sandbox"))
    return parser.parse_args()


def tax_year(default: int = 2025) -> int:
    return int(os.getenv("TAX_ASSISTANT_TAX_YEAR", str(default)))


def print_json(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


args = parse_args()
client = TaxReturnAssistantClient()
profile = FilingProfile(
    tax_year=tax_year(),
    taxpayer_type="business",
    business_income=False,
    has_employees=os.getenv("TAX_ASSISTANT_HAS_EMPLOYEES", "1") != "0",
    paid_suppliers=os.getenv("TAX_ASSISTANT_PAID_SUPPLIERS", "1") != "0",
)
response = client.recommend_forms(profile).to_dict()
response["environment"] = args.env
print_json(response)
for checklist in client.build_checklist(profile):
    print_json(checklist.to_dict())
