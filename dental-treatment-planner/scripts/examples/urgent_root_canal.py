#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os

from dental_treatment_planner import DentalTreatmentPlannerClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate urgent molar root-canal care.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("DTP_ENV", "sandbox"))
    args = parser.parse_args()
    plan = {
        "context": {
            "provider": os.getenv("DTP_PROVIDER", "private"),
            "region": os.getenv("DTP_REGION", "tel_aviv"),
            "start_date": os.getenv("DTP_START_DATE", "01/08/2026"),
        },
        "treatments": [
            {"code": "emergency_visit", "urgency": "emergency"},
            {"code": "exam"},
            {"code": "xray_bitewing"},
            {"code": "root_canal_molar", "tooth": os.getenv("DTP_TOOTH", "46"), "urgency": "urgent"},
            {"code": "crown_porcelain", "tooth": os.getenv("DTP_TOOTH", "46")},
        ],
    }
    result = DentalTreatmentPlannerClient(environment=args.env).estimate(plan)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
