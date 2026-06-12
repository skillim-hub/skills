from __future__ import annotations

import argparse
import json
import os


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("FTIE_ENV", "sandbox"))
    parser.add_argument("--language", choices=["he", "en"], default=os.getenv("FTIE_DEFAULT_LANGUAGE", "he"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = {
        "context": {
            "language": args.language,
            "environment": args.env,
            "business_name": os.getenv("FTIE_BUSINESS_NAME", ""),
            "business_type": "authorized_dealer",
            "document_type": "tax_invoice",
        },
        "lines": [
            {"description": "הקמת דף נחיתה", "quantity": "1", "unit_price": "1200", "vat_rate": "18"},
            {"description": "רכישת תמונת מאגר עבור הלקוח", "quantity": "1", "unit_price": "40", "vat_rate": "18", "reimbursable": True},
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
