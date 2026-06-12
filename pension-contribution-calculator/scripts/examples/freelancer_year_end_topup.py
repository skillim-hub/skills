#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os

import pension_contribution_calculator_client as pcc

parser = argparse.ArgumentParser(description="Freelancer year-end top-up example")
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PCC_ENV", "sandbox"))
args = parser.parse_args()

annual_income = float(os.getenv("PCC_ANNUAL_INCOME", "240000"))
age = int(os.getenv("PCC_AGE", "42"))
pension_deposit = float(os.getenv("PCC_PENSION_DEPOSIT", "12000"))
hishtalmut_deposit = float(os.getenv("PCC_HISHTALMUT_DEPOSIT", "20566"))
result = pcc.self_employed_contributions(
    annual_income,
    age=age,
    annual_pension_deposit=pension_deposit,
    annual_hishtalmut_deposit=hishtalmut_deposit,
)
record = pcc.create_calculation_record("self_employed", result, environment=args.env, source="example")
print(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True))
