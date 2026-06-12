from __future__ import annotations

import argparse
import json
import os

from loan_amortization_planner import LoanScenario, build_schedule, compare_scenarios


def env_value(name: str, default: str) -> str:
    return os.environ.get(name, default)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--env", choices=["sandbox", "production"], default=os.environ.get("LOAN_PLANNER_ENV", "sandbox"))
    return p


def main() -> None:
    args = parser().parse_args()
    payload = {
        "name": env_value("LOAN_NAME", "CPI linked renovation"),
        "principal": env_value("LOAN_PRINCIPAL", "180000"),
        "term_months": int(env_value("LOAN_TERM_MONTHS", "84")),
        "start_date": env_value("LOAN_START_DATE", "01/08/2026"),
        "rate_type": "cpi",
        "annual_interest_rate": env_value("LOAN_ANNUAL_INTEREST_RATE", "0.042"),
        "annual_cpi_rate": env_value("LOAN_ANNUAL_CPI_RATE", "0.025"),
    }
    scenario = LoanScenario.from_mapping(payload)
    schedule = build_schedule(scenario)
    print(json.dumps({{"env": args.env, "summary": schedule.summary.as_dict()}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
