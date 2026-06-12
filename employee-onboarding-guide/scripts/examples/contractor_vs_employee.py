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
supplier = EmployeeProfile(
    full_name=os.getenv("ONBOARDING_SUPPLIER_NAME", "Supplier Example"),
    start_date=os.getenv("ONBOARDING_START_DATE", "01-09-2026"),
    employment_type="contractor",
    role=os.getenv("ONBOARDING_ROLE", "Marketing Consultant"),
)
unclear = EmployeeProfile(
    full_name=os.getenv("ONBOARDING_EMPLOYEE_NAME", "Classification Review Example"),
    start_date=os.getenv("ONBOARDING_START_DATE", "01-09-2026"),
    employment_type="unknown",
    role="Operations Assistant",
)
print(json.dumps({
    "environment": env,
    "supplier_validation": validate_profile(supplier).to_dict(),
    "unclear_validation": validate_profile(unclear).to_dict()
}, ensure_ascii=False, indent=2))
