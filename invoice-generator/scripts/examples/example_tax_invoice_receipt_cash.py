#!/usr/bin/env python3
"""Paid-on-the-spot tax invoice receipt scenario."""

from __future__ import annotations

import argparse
import json
import os

from invoice_generator import DocumentSpec, sample_tax_invoice_receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("INVOICE_GENERATOR_ENV", "sandbox"))
    args = parser.parse_args()

    data = sample_tax_invoice_receipt()
    data["payments"] = [{"method": "cash", "amount": "21240.00", "reference": "CASH-001", "paid_at": "15/06/2026"}]
    spec = DocumentSpec.from_dict(data)
    output = {"environment": args.env, "validation": spec.validate().to_dict(), "totals": spec.calculate_totals().to_dict(), "document": spec.to_dict()}
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
