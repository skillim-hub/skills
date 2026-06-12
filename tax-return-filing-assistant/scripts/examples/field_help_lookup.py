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
response = {"environment": args.env, "fields": []}
for form, field_id in [("1301", "business_income"), ("135", "refund_reason"), ("856", "withholding_rate")]:
    response["fields"].append(client.get_field_help(form, field_id).to_dict())
print_json(response)
