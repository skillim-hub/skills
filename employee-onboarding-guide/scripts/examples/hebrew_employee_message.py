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
name = os.getenv("ONBOARDING_EMPLOYEE_NAME", "דנה לוי")
due_date = os.getenv("ONBOARDING_DUE_DATE", "25/08/2026")
message = generate_employee_message(name, due_date, "he")
print(json.dumps({"environment": env, "message": message}, ensure_ascii=False, indent=2))
