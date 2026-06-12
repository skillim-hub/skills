from __future__ import annotations

import argparse
import json
import os

from business_registration_assistant import BusinessIntake, BusinessRegistrationClient


def parser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("BRA_ENV", "sandbox"))
    return p


def ceiling(default: float = 122833.0) -> float:
    return float(os.getenv("BRA_OSEK_PATUR_CEILING_NIS", str(default)))


def print_json(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))

args = parser("Late registration review scenario").parse_args()
client = BusinessRegistrationClient()
intake = BusinessIntake(
    activity_description=os.getenv("BRA_ACTIVITY", "Fitness coaching"),
    expected_annual_turnover_nis=float(os.getenv("BRA_TURNOVER_NIS", "30000")),
    expected_monthly_profit_nis=float(os.getenv("BRA_MONTHLY_PROFIT_NIS", "2500")),
    current_osek_patur_ceiling_nis=ceiling(),
    actual_start_date=os.getenv("BRA_ACTUAL_START_DATE", "15/04/2026"),
    registration_date=os.getenv("BRA_REGISTRATION_DATE", "01/06/2026"),
)
print_json({"environment": args.env, "plan": client.build_full_plan(intake).to_dict()})
