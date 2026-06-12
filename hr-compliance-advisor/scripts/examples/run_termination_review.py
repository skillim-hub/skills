from __future__ import annotations

import argparse
import json
import os

from hr_compliance_advisor import EmployeeFacts, HRComplianceClient, config_from_env

SCENARIO = {"worker_type":"employee","sector":"general","monthly_salary_ils":9000,"tenure_months":30,"termination_reason":"Immediate dismissal without hearing.","notice_days_given":7}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a local HR compliance scenario.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.environ.get("HR_COMPLIANCE_ENV", "sandbox"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = HRComplianceClient(config_from_env(os.environ))
    report = client.review(EmployeeFacts(**SCENARIO))
    report["environment"] = args.env
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
