from __future__ import annotations

import argparse
import json
import os

from prescription_renewal_assistant import (
    Fulfillment,
    PrescriptionRenewalClient,
    RenewalCase,
    build_doctor_message,
    expense_record,
    pharmacy_checklist,
    triage_case,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
    return parser.parse_args()


def config(args: argparse.Namespace) -> dict[str, str | None]:
    return {
        "env": args.env,
        "api_base_url": os.environ.get("PRA_API_BASE_URL"),
        "api_token_present": str(bool(os.environ.get("PRA_API_TOKEN"))).lower(),
        "default_kupat_cholim": os.environ.get("PRA_DEFAULT_KUPAT_CHOLIM", "Maccabi"),
        "default_pharmacy": os.environ.get("PRA_DEFAULT_PHARMACY", "Super-Pharm"),
    }


def dump(payload: object) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))

args = parse_args()
cfg = config(args)
case = RenewalCase(
    kupat_cholim=cfg["default_kupat_cholim"] or "Clalit",
    medication_name="as shown in portal",
    supply_days=3,
    repeats_left=1,
    preferred_fulfillment=Fulfillment.DELIVERY,
    needs_cold_chain=True,
    pharmacy=cfg["default_pharmacy"],
    consent_confirmed=True,
)
dump({
    "config": cfg,
    "triage": triage_case(case).to_dict(),
    "checklist": pharmacy_checklist(
        pharmacy=cfg["default_pharmacy"],
        fulfillment=Fulfillment.DELIVERY,
        needs_cold_chain=True,
    ).to_dict(),
})
