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

args = parser("Digital marketplace seller accountant handoff scenario").parse_args()
client = BusinessRegistrationClient()
intake = BusinessIntake(
    activity_description=os.getenv("BRA_ACTIVITY", "Handmade jewelry sales on Etsy"),
    expected_annual_turnover_nis=float(os.getenv("BRA_TURNOVER_NIS", "95000")),
    expected_monthly_profit_nis=float(os.getenv("BRA_MONTHLY_PROFIT_NIS", "4500")),
    current_osek_patur_ceiling_nis=ceiling(),
    foreign_clients=True,
    online_sales=True,
)
print_json({"environment": args.env, "handoff": client.accountant_handoff(intake)})
