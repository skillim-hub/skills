#!/usr/bin/env python3
"""Generate a conservative Form 856 staging CSV from payments and certificates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from withholding_tax_compliance import (
    build_form856_staging_rows,
    load_certificates_json,
    load_payments_csv,
    validate_form856_submission_inputs,
    write_staging_csv,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Israeli Form 856 staging CSV")
    parser.add_argument("--payments", required=True, help="CSV with payment_id,supplier_tax_id,payment_date,amount_before_vat_ils,vat_ils")
    parser.add_argument("--certificates", required=True, help="JSON array of supplier withholding certificates")
    parser.add_argument("--out", required=True, help="Output staging CSV path")
    parser.add_argument("--include-vat-in-base", action="store_true", help="Use only if accountant/legal workflow requires VAT in base")
    parser.add_argument("--issues-json", help="Optional path to write validation issues JSON")
    args = parser.parse_args()

    payments = load_payments_csv(args.payments)
    certificates = load_certificates_json(args.certificates)
    rows = build_form856_staging_rows(payments, certificates, include_vat_in_base=args.include_vat_in_base)
    issues = validate_form856_submission_inputs(rows)
    write_staging_csv(rows, args.out)

    if args.issues_json:
        Path(args.issues_json).write_text(json.dumps(issues, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote {len(rows)} staging rows to {args.out}")
    if issues:
        print(f"validation issues: {len(issues)}")
        return 2
    print("validation issues: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
