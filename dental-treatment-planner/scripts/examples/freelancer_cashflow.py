#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict

from dental_treatment_planner import DentalTreatmentPlannerClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Estimate monthly cash-flow exposure for a freelancer.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("DTP_ENV", "sandbox"))
    args = parser.parse_args()
    plan = {
        "context": {
            "provider": os.getenv("DTP_PROVIDER", "private"),
            "region": os.getenv("DTP_REGION", "center"),
            "start_date": os.getenv("DTP_START_DATE", "01/09/2026"),
            "max_visits_per_month": int(os.getenv("DTP_MAX_VISITS_PER_MONTH", "2")),
            "insurance": {"discount_pct": 15, "annual_limit_ils": 2500, "used_annual_ils": 1000},
        },
        "treatments": [
            {"code": "exam"},
            {"code": "panoramic_xray"},
            {"code": "implant"},
            {"code": "implant_crown"},
        ],
    }
    result = DentalTreatmentPlannerClient(environment=args.env).estimate(plan)
    payments: dict[str, float] = defaultdict(float)
    per_visit = float(result.total_patient_ils) / max(result.visits, 1)
    for entry in result.schedule:
        month = entry["date"][3:10]
        payments[month] += per_visit
    print(json.dumps({"estimate": result.to_dict(), "monthly_cashflow": payments}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
