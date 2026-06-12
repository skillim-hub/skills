from __future__ import annotations

import argparse
import json
import os

from parking_fine_checker import FineLookupRequest, ParkingFineClient, ParkingFineAsyncClient, assess_case, build_checklist, detect_duplicates, approval_memo


def base_url_for(env: str) -> str:
    if env == "production":
        return os.getenv("PARKING_FINE_BASE_URL_PRODUCTION", "mock://local")
    return os.getenv("PARKING_FINE_BASE_URL_SANDBOX", "mock://local")


def token_for(env: str) -> str | None:
    if env == "production":
        return os.getenv("PARKING_FINE_TOKEN_PRODUCTION")
    return os.getenv("PARKING_FINE_TOKEN_SANDBOX")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PARKING_FINE_ENV", "sandbox"))
    return p

args = parser().parse_args()
case_id = os.getenv("PARKING_FINE_CASE_ID", "20260602-1234567-1001")
memo = approval_memo(
    case_id=case_id,
    issuer_name=os.getenv("PARKING_FINE_ISSUER_NAME", "Example Municipality"),
    vehicle_number=os.getenv("PARKING_FINE_VEHICLE_NUMBER", "12-345-67"),
    notice_number=os.getenv("PARKING_FINE_NOTICE_NUMBER", "1001"),
    amount_ils=os.getenv("PARKING_FINE_AMOUNT_ILS", "250.00"),
    due_date=os.getenv("PARKING_FINE_DUE_DATE", "08/06/2026"),
    approver=os.getenv("PARKING_FINE_APPROVER", "Office manager"),
)
print(json.dumps({"environment": args.env, "memo": memo}, ensure_ascii=False, indent=2))
