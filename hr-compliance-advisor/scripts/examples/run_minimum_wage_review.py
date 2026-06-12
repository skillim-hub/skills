from __future__ import annotations

import argparse
import json
import os

from hr_compliance_advisor import EmployeeFacts, HRComplianceClient, config_from_env

SCENARIO = {"worker_type":"employee","sector":"retail","hourly_rate_ils":31.0,"weekly_hours":38,"tenure_months":10,"has_pension_arrangement":False,"contract_text":"Closing time is unpaid."}


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
