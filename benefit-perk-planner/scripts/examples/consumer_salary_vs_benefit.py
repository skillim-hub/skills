from __future__ import annotations

import argparse
import json
import os

from benefit_perk_planner_client import BenefitPlannerClient, BenefitRequest, request_from_env


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Consumer salary versus benefit scenario")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("BENEFIT_PLANNER_ENV", "sandbox"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    request = request_from_env("consumer", environment=args.env)
    plan = BenefitPlannerClient(environment=args.env).plan(request)
    print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
