from __future__ import annotations

import argparse
import json
import os

from loan_amortization_planner import LoanScenario, compare_scenarios


def env_value(name: str, default: str) -> str:
    return os.environ.get(name, default)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.environ.get("LOAN_PLANNER_ENV", "sandbox"))
    args = parser.parse_args()

    principal = env_value("LOAN_PRINCIPAL", "300000")
    term = int(env_value("LOAN_TERM_MONTHS", "60"))
    start = env_value("LOAN_START_DATE", "01/07/2026")
    offers = [
        LoanScenario.from_mapping({"name": "fixed 6.4", "principal": principal, "term_months": term, "start_date": start, "annual_interest_rate": env_value("FIXED_RATE", "0.064")}),
        LoanScenario.from_mapping({"name": "prime plus 1.2", "principal": principal, "term_months": term, "start_date": start, "rate_type": "prime", "prime_rate": env_value("PRIME_RATE", "0.0525"), "prime_margin": env_value("PRIME_MARGIN", "0.012")}),
        LoanScenario.from_mapping({"name": "cpi 3.9", "principal": principal, "term_months": term, "start_date": start, "rate_type": "cpi", "annual_interest_rate": env_value("CPI_RATE", "0.039"), "annual_cpi_rate": env_value("ANNUAL_CPI_RATE", "0.025")}),
    ]
    print(json.dumps({"env": args.env, "comparison": compare_scenarios(offers)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
