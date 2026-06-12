#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os

from dental_treatment_planner import DentalTreatmentPlannerClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage imaging, implant placement, and prosthetic restoration.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("DTP_ENV", "sandbox"))
    args = parser.parse_args()
    plan = {
        "context": {
            "provider": os.getenv("DTP_PROVIDER", "clalit_smile"),
            "region": os.getenv("DTP_REGION", "jerusalem"),
            "start_date": os.getenv("DTP_START_DATE", "15/10/2026"),
        },
        "treatments": [
            {"code": "exam"},
            {"code": "panoramic_xray"},
            {"code": "implant", "tooth": os.getenv("DTP_TOOTH", "36")},
            {"code": "implant_crown", "tooth": os.getenv("DTP_TOOTH", "36")},
        ],
    }
    result = DentalTreatmentPlannerClient(environment=args.env).estimate(plan)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
