from __future__ import annotations

import argparse
import json
import os

from free_text_invoice_explanation import InvoiceExplanationClient


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
            "business_type": "company",
            "document_type": "invoice_receipt",
        },
        "lines": [
            {
                "description": "מנוי חודשי למערכת ניהול לקוחות",
                "quantity": "1",
                "unit_price": "199",
                "vat_rate": "18",
                "service_period": "01/03/2026-31/03/2026",
            }
        ],
    }
    result = InvoiceExplanationClient().explain_payload(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
