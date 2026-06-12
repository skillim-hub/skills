from __future__ import annotations

import argparse
import json
import os

from benefit_perk_planner_client import BenefitPlannerClient, BenefitRequest, request_from_env


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hybrid employer retention scenario")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("BENEFIT_PLANNER_ENV", "sandbox"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    request = BenefitRequest(
        entity_type="employer",
        employee_count=int(os.getenv("BENEFIT_PLANNER_EMPLOYEE_COUNT", "12")),
        monthly_budget_ils=float(os.getenv("BENEFIT_PLANNER_BUDGET_ILS", "15000")),
        goals=[goal for goal in os.getenv("BENEFIT_PLANNER_GOALS", "retention,equity").split(",") if goal],
        work_model=os.getenv("BENEFIT_PLANNER_WORK_MODEL", "hybrid"),
        existing_benefits=[value for value in os.getenv("BENEFIT_PLANNER_EXISTING_BENEFITS", "mandatory pension").split(",") if value],
        location=os.getenv("BENEFIT_PLANNER_LOCATION", "Tel Aviv"),
        wants_keren_hishtalmut=os.getenv("BENEFIT_PLANNER_WANTS_KEREN_HISHTALMUT", "true").lower() == "true",
    )
    plan = BenefitPlannerClient(environment=args.env).plan(request)
    print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
