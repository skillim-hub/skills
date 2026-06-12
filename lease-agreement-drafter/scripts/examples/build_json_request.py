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
    os.getenv("LEASE_DRAFTER_API_KEY", "")
    request = {
        "landlord": {"name": "שם המשכיר", "id_number": ""},
        "tenant": {"name": "שם השוכר", "id_number": ""},
        "property": {"property_type": "apartment", "address": "רחוב ומספר", "city": "עיר"},
        "terms": {"start_date": "01/08/2026", "end_date": "31/07/2027", "monthly_rent_ils": 5000, "security_deposit_ils": 10000},
        "language": "he",
        "special_conditions": ["אין להחזיק בעלי חיים ללא הסכמה בכתב, למעט חיית שירות לפי דין."],
    }
    emit({"environment": args.env, "request": request}, args.output)


if __name__ == "__main__":
    main()
