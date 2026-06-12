#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from social_security_benefit_checker import ApplicantProfile, LocalProfileStore, SocialSecurityBenefitChecker


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Laid-off employee unemployment scenario")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.environ.get("BENEFIT_CHECKER_ENV", "sandbox"))
    parser.add_argument("--store-dir", default=os.environ.get("BENEFIT_CHECKER_STORE"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    store = LocalProfileStore(directory=args.store_dir, environment=args.env)
    checker = SocialSecurityBenefitChecker(environment=args.env, store=store)
    default_city = os.environ.get("BENEFIT_CHECKER_DEFAULT_CITY", "")
    profile = ApplicantProfile.from_mapping({'age': 44, 'resident': True, 'employment_status': 'unemployed', 'monthly_income': 10500, 'children_count': 1, 'qualifying_months': 16, 'termination_reason': 'laid_off', 'registered_employment_service': True, 'birth_dates': ['22/03/2016']})
    payload = {"scenario": "laid_off_employee", "environment": args.env, "result": checker.check_benefit("unemployment", profile).to_dict()}
    if default_city:
        payload["context_note"] = f"Default city from environment: {default_city}"
    output = json.dumps(payload, ensure_ascii=False, indent=2)
    output_path = os.environ.get("BENEFIT_CHECKER_OUTPUT")
    if output_path:
        Path(output_path).write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
