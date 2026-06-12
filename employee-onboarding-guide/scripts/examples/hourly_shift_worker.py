from __future__ import annotations

import argparse
import json
import os

from employee_onboarding_guide_client import EmployeeProfile, create_record, generate_checklist, generate_employee_message, validate_profile

def parse_env() -> str:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("ONBOARDING_ENV", "sandbox"))
    return parser.parse_args().env

env = parse_env()
profile = EmployeeProfile(
    full_name=os.getenv("ONBOARDING_EMPLOYEE_NAME", "Noa Cohen"),
    start_date=os.getenv("ONBOARDING_START_DATE", "01-09-2026"),
    role=os.getenv("ONBOARDING_ROLE", "Cafe Shift Worker"),
    salary_type="hourly",
    hourly_rate_nis=float(os.getenv("ONBOARDING_HOURLY_RATE_NIS", "55")),
    has_other_employer=True,
    has_active_pension=False,
    bank_details_received=False,
    employment_notice_status="missing",
)
print(json.dumps({"environment": env, "validation": validate_profile(profile).to_dict(), "checklist": generate_checklist(profile)}, ensure_ascii=False, indent=2))
