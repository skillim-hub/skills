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
    full_name=os.getenv("ONBOARDING_EMPLOYEE_NAME", "Dana Levi"),
    start_date=os.getenv("ONBOARDING_START_DATE", "01-09-2026"),
    role=os.getenv("ONBOARDING_ROLE", "Sales Coordinator"),
    salary_type="monthly",
    monthly_salary_nis=float(os.getenv("ONBOARDING_MONTHLY_SALARY_NIS", "12000")),
    has_active_pension=True,
    pension_fund_name=os.getenv("ONBOARDING_PENSION_FUND", "Example Pension Fund"),
    bank_details_received=True,
    employment_notice_status="drafted",
)
response = create_record(profile, environment=env)
print(json.dumps({"environment": env, "create_response": response, "validation": validate_profile(profile).to_dict()}, ensure_ascii=False, indent=2))
