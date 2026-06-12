#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os

from dental_treatment_planner import DentalTreatmentPlannerClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate preventive pediatric dental care.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("DTP_ENV", "sandbox"))
    args = parser.parse_args()
    plan = {
        "context": {
            "provider": os.getenv("DTP_PROVIDER", "maccabident"),
            "region": os.getenv("DTP_REGION", "south"),
            "start_date": os.getenv("DTP_START_DATE", "20/07/2026"),
        },
        "treatments": [
            {"code": "exam"},
            {"code": "cleaning"},
            {"code": "fluoride_child"},
            {"code": "sealant_child", "quantity": 2},
        ],
    }
    result = DentalTreatmentPlannerClient(environment=args.env).estimate(plan)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
