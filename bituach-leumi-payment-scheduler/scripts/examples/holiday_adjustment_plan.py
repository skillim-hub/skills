#!/usr/bin/env python3
"""Holiday adjustment planning scenario."""

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
    payer_name = os.getenv("BL_PAYER_NAME", "נותן שירות עצמאי")
    income = float(os.getenv("BL_MONTHLY_INCOME_NIS", "9000"))
    holidays = frozenset({date(2026, 6, 15)})
    profile = BusinessProfile(payer_name=payer_name, business_type=BusinessType.SELF_EMPLOYED, monthly_income_nis=income)
    options = ScheduleOptions(start_month=date(2026, 5, 1), months=2, holidays=holidays, adjustment_policy=AdjustmentPolicy.NEXT_BUSINESS_DAY)
    plan = generate_payment_plan(profile, options)
    print_json(plan_record(plan, environment=args.env))


if __name__ == "__main__":
    main()
