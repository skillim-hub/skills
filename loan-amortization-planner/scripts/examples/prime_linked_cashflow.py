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
        "name": env_value("LOAN_NAME", "prime working capital"),
        "principal": env_value("LOAN_PRINCIPAL", "120000"),
        "term_months": int(env_value("LOAN_TERM_MONTHS", "36")),
        "start_date": env_value("LOAN_START_DATE", "15/06/2026"),
        "rate_type": "prime",
        "prime_rate": env_value("LOAN_PRIME_RATE", "0.0525"),
        "prime_margin": env_value("LOAN_PRIME_MARGIN", "0.018"),
        "rate_changes": {"13": env_value("LOAN_PERIOD_13_RATE", "0.085")},
    }
    scenario = LoanScenario.from_mapping(payload)
    schedule = build_schedule(scenario)
    print(json.dumps({{"env": args.env, "summary": schedule.summary.as_dict()}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
