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
profile = FilingProfile(tax_year=tax_year(), is_online=os.getenv("TAX_ASSISTANT_ONLINE", "1") != "0")
for form in ["1301", "126", "856", "6111"]:
    deadline = client.calculate_deadlines(profile, [form])[0].to_dict()
    deadline["environment"] = args.env
    print_json(deadline)
