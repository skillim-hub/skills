from __future__ import annotations

import argparse
import json
import os

from benefit_perk_planner_client import BenefitPlannerClient, BenefitRequest, request_from_env


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Contractor classification risk scenario")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("BENEFIT_PLANNER_ENV", "sandbox"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    request = BenefitRequest(
        entity_type="employer",
        employee_count=int(os.getenv("BENEFIT_PLANNER_EMPLOYEE_COUNT", "6")),
        monthly_budget_ils=float(os.getenv("BENEFIT_PLANNER_BUDGET_ILS", "4000")),
        includes_contractors=os.getenv("BENEFIT_PLANNER_INCLUDES_CONTRACTORS", "true").lower() == "true",
        existing_benefits=[value for value in os.getenv("BENEFIT_PLANNER_EXISTING_BENEFITS", "mandatory pension").split(",") if value],
    )
    plan = BenefitPlannerClient(environment=args.env).plan(request)
    print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
