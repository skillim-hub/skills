#!/usr/bin/env python3
"""JSON configuration workflow scenario."""

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
    config = {
        "profile": {
            "payer_name": os.getenv("BL_PAYER_NAME", "חשבון משק בית"),
            "business_type": os.getenv("BL_PAYER_TYPE", "consumer"),
            "amount_override_nis": float(os.getenv("BL_AMOUNT_NIS", "350")),
        },
        "options": {"start_month": os.getenv("BL_START_MONTH", "2026-01"), "months": int(os.getenv("BL_MONTHS", "8"))},
    }
    from bituach_leumi_payment_scheduler import plan_from_mapping
    plan = plan_from_mapping(config)
    print_json({"environment": args.env, "config": config, "record": plan_record(plan, environment=args.env)})


if __name__ == "__main__":
    main()
