#!/usr/bin/env python3
"""Arrears catch-up payment scenario."""

from __future__ import annotations

import argparse
import json
import os
from datetime import date

from bituach_leumi_payment_scheduler import (
    AdjustmentPolicy,
    BusinessProfile,
    BusinessType,
    ScheduleOptions,
    generate_payment_plan,
    plan_record,
    to_csv,
    to_ics,
)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("BL_ENV", "sandbox"))
    return p


def print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def main() -> None:
    args = parser().parse_args()
    payer_name = os.getenv("BL_PAYER_NAME", "הסדר חוב")
    amount = float(os.getenv("BL_AMOUNT_NIS", "600"))
    profile = BusinessProfile(payer_name=payer_name, business_type=BusinessType.CONSUMER, amount_override_nis=amount)
    options = ScheduleOptions(start_month=date(2026, 1, 1), months=10, reminder_days_before=(7, 2, 1))
    plan = generate_payment_plan(profile, options)
    print_json(plan_record(plan, environment=args.env))


if __name__ == "__main__":
    main()
