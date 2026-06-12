from __future__ import annotations

import argparse
import asyncio
import json
import os

from benefit_perk_planner_client import AsyncBenefitPlannerClient, BenefitPlannerClient, BenefitRequest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Async startup plan scenario")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("BENEFIT_PLANNER_ENV", "sandbox"))
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    request = BenefitRequest(
        entity_type="employer",
        employee_count=int(os.getenv("BENEFIT_PLANNER_EMPLOYEE_COUNT", "22")),
        monthly_budget_ils=float(os.getenv("BENEFIT_PLANNER_BUDGET_ILS", "26400")),
        goals=[goal for goal in os.getenv("BENEFIT_PLANNER_GOALS", "retention").split(",") if goal],
        work_model=os.getenv("BENEFIT_PLANNER_WORK_MODEL", "hybrid"),
    )
    client = AsyncBenefitPlannerClient(BenefitPlannerClient(environment=args.env))
    plan = await client.plan(request)
    print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
