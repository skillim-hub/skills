#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from privacy_compliance_checker import PrivacyComplianceCheckerClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Assess a customer-club workflow.")
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("PCC_ENV", "sandbox"))
    parser.add_argument("--state-dir", default=os.getenv("PCC_STATE_DIR", ".pcc-state"))
    parser.add_argument("--profile", default=os.getenv("PCC_PROFILE", "default"))
    parser.add_argument("--save", action="store_true", help="Persist the assessment and print the saved response.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = {'record_count': 18000, 'authorized_users': 4, 'sector': 'retail', 'purposes': ['loyalty benefits', 'receipts', 'direct marketing'], 'lawful_basis': 'consent', 'direct_marketing': True, 'uses_tracking': True, 'cross_border': True, 'destinations': ['United States'], 'processors': ['email delivery provider', 'analytics provider'], 'retention_months': 36}
    payload["business_name"] = f'Neighborhood customer club ({args.profile})'
    client = PrivacyComplianceCheckerClient(environment=args.env, state_dir=Path(args.state_dir))
    if args.save:
        output = client.create(payload)
    else:
        output = client.assess(payload).to_dict()
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
