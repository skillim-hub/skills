"""Command line interface for the Bituach Leumi estimator."""

from __future__ import annotations

import argparse
import json
from .bituach_leumi_estimator import add_vat, estimate_monthly


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Estimate 2026 Israeli self-employed Bituach Leumi contributions.")
    parser.add_argument("--monthly-income", type=float, required=True, help="Monthly self-employed income/profit in ILS")
    parser.add_argument("--months", type=int, default=1, help="Number of months to estimate, 1-12")
    parser.add_argument("--year", type=int, default=2026, help="Regulatory year; only 2026 is bundled")
    parser.add_argument("--add-vat", type=float, default=None, help="Optional net amount to add standard VAT to")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.year != 2026:
        raise SystemExit("Only 2026 is bundled in this web-validated package.")
    payload = {"contributions": estimate_monthly(args.monthly_income, args.months).to_dict()}
    if args.add_vat is not None:
        payload["vat"] = add_vat(args.add_vat, "2026-01-01")
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
