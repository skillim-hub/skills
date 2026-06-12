#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os

import pension_contribution_calculator_client as pcc

parser = argparse.ArgumentParser(description="Employee pension example")
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PCC_ENV", "sandbox"))
args = parser.parse_args()

gross_salary = float(os.getenv("PCC_GROSS_SALARY", "12000"))
result = pcc.employee_contributions(gross_salary, include_hishtalmut=os.getenv("PCC_HISHTALMUT", "false").lower() == "true")
record = pcc.create_calculation_record("employee", result, environment=args.env, source="example")
print(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True))
