#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os

from dental_treatment_planner import DentalTreatmentPlannerClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare routine consumer care across provider profiles.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("DTP_ENV", "sandbox"))
    args = parser.parse_args()
    region = os.getenv("DTP_REGION", "center")
    plan = {
        "context": {"region": region, "start_date": os.getenv("DTP_START_DATE", "15/07/2026")},
        "treatments": [{"code": "exam"}, {"code": "xray_bitewing"}, {"code": "cleaning"}],
    }
    results = DentalTreatmentPlannerClient(environment=args.env).compare_providers(plan)
    payload = [result.to_dict() for result in results]
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
