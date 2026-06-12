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
        "name": env_value("LOAN_NAME", "extra repayment after VAT refund"),
        "principal": env_value("LOAN_PRINCIPAL", "90000"),
        "term_months": int(env_value("LOAN_TERM_MONTHS", "48")),
        "start_date": env_value("LOAN_START_DATE", "01/07/2026"),
        "annual_interest_rate": env_value("LOAN_ANNUAL_INTEREST_RATE", "0.07"),
        "extra_payments": {"7": env_value("LOAN_PERIOD_7_EXTRA_PAYMENT", "25000")},
        "early_payment_fee": env_value("LOAN_EARLY_PAYMENT_FEE", "350"),
    }
    scenario = LoanScenario.from_mapping(payload)
    schedule = build_schedule(scenario)
    print(json.dumps({{"env": args.env, "summary": schedule.summary.as_dict()}}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
