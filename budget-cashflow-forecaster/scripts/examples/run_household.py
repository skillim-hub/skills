from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from budget_cashflow_forecaster import CashFlowForecaster


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("BCF_ENV", "sandbox"))
    args = parser.parse_args()
    scenario_path = Path(__file__).with_name("household_budget.json")
    data = json.loads(scenario_path.read_text(encoding="utf-8"))
    if os.getenv("BCF_OPENING_BALANCE"):
        data["opening_balance"] = float(os.environ["BCF_OPENING_BALANCE"])
    result = CashFlowForecaster().forecast({**data, "environment": args.env})
    print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
