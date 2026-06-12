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
issuer_type = os.getenv("PARKING_FINE_ISSUER_TYPE", "municipality")
decision = assess_case(
    issuer_type=issuer_type,
    status=os.getenv("PARKING_FINE_STATUS", "verified_unpaid"),
    payment_app_matches=os.getenv("PARKING_FINE_PAYMENT_APP_MATCHES", "true").lower() == "true",
)
payload = {
    "environment": args.env,
    "decision": decision,
    "next_steps": build_checklist(issuer_type),
}
print(json.dumps(payload, ensure_ascii=False, indent=2))
