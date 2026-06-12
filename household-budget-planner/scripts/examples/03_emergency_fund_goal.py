from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from household_budget_planner import HouseholdBudgetPlannerClient, create_sample_plan, extract_vat, format_shekel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("HBP_ENV", "sandbox"))
    parser.add_argument("--output", default=os.getenv("HBP_OUTPUT", ""))
    return parser.parse_args()


def emit(payload: dict, output: str = "") -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if output:
        Path(output).write_text(text + "\n", encoding="utf-8")
    print(text)


def main() -> None:
    args = parse_args()
    month = os.getenv("HBP_MONTH", "05-2026")
    target = float(os.getenv("HBP_TARGET_AMOUNT", "30000"))
    current = float(os.getenv("HBP_CURRENT_AMOUNT", "18000"))
    due = os.getenv("HBP_DUE_DATE", "31-12-2026")
    client = HouseholdBudgetPlannerClient.for_month(month, environment=args.env)
    client.add_savings_goal(name="קרן חירום", target_amount=target, current_amount=current, due_date=due)
    emit(
        {
            "environment": args.env,
            "goal_progress": [item.__dict__ for item in client.goal_progress()],
        },
        args.output,
    )


if __name__ == "__main__":
    main()
