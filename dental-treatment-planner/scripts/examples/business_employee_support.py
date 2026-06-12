#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os

from dental_treatment_planner import DentalTreatmentPlannerClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate a small-business employee dental-support budget.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("DTP_ENV", "sandbox"))
    args = parser.parse_args()
    employee_count = int(os.getenv("DTP_EMPLOYEES", "5"))
    plan = {
        "context": {
            "provider": os.getenv("DTP_PROVIDER", "private"),
            "region": os.getenv("DTP_REGION", "center"),
            "start_date": os.getenv("DTP_START_DATE", "01/11/2026"),
        },
        "treatments": [{"code": "exam", "quantity": employee_count}, {"code": "cleaning", "quantity": employee_count}],
    }
    result = DentalTreatmentPlannerClient(environment=args.env).estimate(plan)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
