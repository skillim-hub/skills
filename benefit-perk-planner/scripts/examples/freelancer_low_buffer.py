from __future__ import annotations

import argparse
import json
import os

from benefit_perk_planner_client import BenefitPlannerClient, BenefitRequest, request_from_env


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Freelancer low cash-buffer scenario")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("BENEFIT_PLANNER_ENV", "sandbox"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    request = BenefitRequest(
        entity_type="freelancer",
        monthly_income_ils=float(os.getenv("BENEFIT_PLANNER_MONTHLY_INCOME_ILS", "28000")),
        cash_buffer_months=float(os.getenv("BENEFIT_PLANNER_CASH_BUFFER_MONTHS", "2")),
        monthly_budget_ils=float(os.getenv("BENEFIT_PLANNER_BUDGET_ILS", "1800")),
        goals=[goal for goal in os.getenv("BENEFIT_PLANNER_GOALS", "tax_efficiency,wellbeing").split(",") if goal],
    )
    plan = BenefitPlannerClient(environment=args.env).plan(request)
    print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
