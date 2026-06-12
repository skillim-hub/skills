#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import io
import json
import os

import pension_contribution_calculator_client as pcc

parser = argparse.ArgumentParser(description="Payroll export example")
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PCC_ENV", "sandbox"))
args = parser.parse_args()

employees = [
    {"name": os.getenv("PCC_EMPLOYEE_1_NAME", "Employee A"), "gross": float(os.getenv("PCC_EMPLOYEE_1_GROSS", "10000"))},
    {"name": os.getenv("PCC_EMPLOYEE_2_NAME", "Employee B"), "gross": float(os.getenv("PCC_EMPLOYEE_2_GROSS", "18000"))},
]
buffer = io.StringIO()
writer = csv.DictWriter(buffer, fieldnames=["name", "gross", "employee_pension", "employer_pension", "employer_severance"])
writer.writeheader()
for employee in employees:
    result = pcc.employee_contributions(employee["gross"], include_hishtalmut=True)
    writer.writerow({
        "name": employee["name"],
        "gross": result.gross_salary,
        "employee_pension": result.employee_pension,
        "employer_pension": result.employer_pension,
        "employer_severance": result.employer_severance,
    })
record = {"environment": args.env, "kind": "payroll_export", "csv": buffer.getvalue()}
print(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True))
