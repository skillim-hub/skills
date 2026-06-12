#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from pension_fund_tracker import PensionFundTrackerClient, records_to_dicts


def build_parser(description: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PENSION_TRACKER_ENV", "sandbox"))
    parser.add_argument("--input", default=os.getenv("PENSION_TRACKER_INPUT", ""))
    return parser


def sample_file() -> Path:
    path = Path(os.getenv("PENSION_TRACKER_SAMPLE_PATH", "/tmp/pension_tracker_sample.csv"))
    path.write_text(
        "מספר קופה,שם קופה,שם גוף מנהל,תאריך דיווח,תשואה 36 חודשים אחרונים,דמי ניהול מצבירה,דמי ניהול מהפקדה\n"
        "12345,קרן א,גוף א,31/12/2025,18.2,0.20,1.50\n"
        "67890,קרן ב,גוף ב,31/12/2025,17.9,0.24,1.20\n",
        encoding="utf-8-sig",
    )
    return path


def resolve_input(value: str) -> Path:
    return Path(value) if value else sample_file()


def print_json(value) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))

args = build_parser("Estimate fee impact from explicit assumptions").parse_args()
client = PensionFundTrackerClient()
result = client.estimate_fee_impact(
    monthly_contribution=float(os.getenv("PENSION_TRACKER_MONTHLY_CONTRIBUTION", "2500")),
    starting_balance=float(os.getenv("PENSION_TRACKER_STARTING_BALANCE", "50000")),
    years=int(os.getenv("PENSION_TRACKER_YEARS", "25")),
    annual_return_pct=float(os.getenv("PENSION_TRACKER_ANNUAL_RETURN_PCT", "4")),
    deposit_fee_pct=float(os.getenv("PENSION_TRACKER_DEPOSIT_FEE_PCT", "1")),
    asset_fee_pct=float(os.getenv("PENSION_TRACKER_ASSET_FEE_PCT", "0.2")),
)
print_json({"env": args.env, "fee_impact": result.__dict__})
