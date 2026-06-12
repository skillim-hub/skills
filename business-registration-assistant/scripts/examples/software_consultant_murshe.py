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

args = parser("Software consultant עוסק מורשה planning scenario").parse_args()
client = BusinessRegistrationClient()
intake = BusinessIntake(
    activity_description=os.getenv("BRA_ACTIVITY", "B2B software consulting"),
    expected_annual_turnover_nis=float(os.getenv("BRA_TURNOVER_NIS", "220000")),
    expected_monthly_profit_nis=float(os.getenv("BRA_MONTHLY_PROFIT_NIS", "15000")),
    current_osek_patur_ceiling_nis=ceiling(),
    clients_require_tax_invoice=True,
    large_vat_bearing_expenses=True,
)
print_json({"environment": args.env, "plan": client.build_full_plan(intake).to_dict()})
