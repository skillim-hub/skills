from __future__ import annotations

import argparse
import json
import os

from healthcare_appointment_booker import HealthcareAppointmentBookerClient, build_request


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("HAB_ENV", "sandbox"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    request = build_request(
        hmo=os.getenv("HAB_HMO", "maccabi"),
        service=os.getenv("HAB_SERVICE", "dermatology skin mole check"),
        city=os.getenv("HAB_CITY", "Rishon LeZion"),
        date_from=os.getenv("HAB_DATE_FROM", "2026-07-01"),
        date_to=os.getenv("HAB_DATE_TO", "2026-07-31"),
        age_group=os.getenv("HAB_AGE_GROUP", "adult"),
        urgency=os.getenv("HAB_URGENCY", "routine"),
        referral_status=os.getenv("HAB_REFERRAL_STATUS", "has_referral"),
        language=os.getenv("HAB_LANGUAGE", "en"),
        accessibility=tuple(filter(None, os.getenv("HAB_ACCESSIBILITY", "wheelchair").split(","))),
        notes=os.getenv("HAB_NOTES", ""),
    )
    plan = HealthcareAppointmentBookerClient().plan(request)
    payload = {
        "environment": args.env,
        "manual_official_channel_required": True,
        "plan": plan.to_dict(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
