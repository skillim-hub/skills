from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from lease_agreement_drafter import LeaseAgreementDrafterClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("LEASE_DRAFTER_ENV", "sandbox"))
    parser.add_argument("--output", type=Path, default=None)
    return parser.parse_args()


def emit(payload: dict, output: Path | None = None) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if output:
        output.write_text(text, encoding="utf-8")
    print(text)


def main() -> None:
    args = parse_args()
    api_key = os.getenv("LEASE_DRAFTER_API_KEY", "")
    client = LeaseAgreementDrafterClient(api_key=api_key, environment=args.env)
    request = {
        "landlord": {"name": "חברת נכסים מרכז בעמ", "is_business": True, "vat_number": "515000111"},
        "tenant": {"name": "סטודיו גל", "is_business": True, "vat_number": "558000222"},
        "property": {"property_type": "office", "address": "דרך מנחם בגין 144", "city": "תל אביב", "area_sqm": 42, "permitted_use": "משרד ייעוץ ועיצוב"},
        "terms": {"start_date": "01/10/2026", "end_date": "30/09/2027", "monthly_rent_ils": 7800, "security_deposit_ils": 23400, "vat_applies": True, "management_fee_ils": 900},
        "language": "he",
    }
    result = client.draft(request)
    emit(result.to_dict(), args.output)


if __name__ == "__main__":
    main()
