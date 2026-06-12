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

args = parser("Migration from עוסק פטור to עוסק מורשה scenario").parse_args()
client = BusinessRegistrationClient()
payload = client.migration_checklist(
    year_to_date_turnover_nis=float(os.getenv("BRA_YTD_TURNOVER_NIS", "110000")),
    forecast_remaining_turnover_nis=float(os.getenv("BRA_FORECAST_TURNOVER_NIS", "40000")),
    current_osek_patur_ceiling_nis=ceiling(),
)
print_json({"environment": args.env, "migration": payload})
