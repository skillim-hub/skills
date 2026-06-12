#!/usr/bin/env python3
"""Underscored client entry point for local script usage."""

from business_registration_assistant.client import *  # noqa: F403
from business_registration_assistant.client import BusinessIntake, BusinessRegistrationClient, dump_json, load_intake

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Business registration preparation helper")
    sub = parser.add_subparsers(dest="command", required=True)

    classify = sub.add_parser("classify")
    classify.add_argument("--activity", required=True)
    classify.add_argument("--turnover", type=float, required=True)
    classify.add_argument("--profit", type=float)
    classify.add_argument("--ceiling", type=float)
    classify.add_argument("--regulated-profession", action="store_true")
    classify.add_argument("--clients-require-tax-invoice", action="store_true")
    classify.add_argument("--foreign-clients", action="store_true")
    classify.add_argument("--currently-employee", action="store_true")
    classify.add_argument("--receives-benefits", action="store_true")

    plan = sub.add_parser("plan")
    plan.add_argument("--input", required=True)

    args = parser.parse_args()
    client = BusinessRegistrationClient()
    if args.command == "classify":
        intake = BusinessIntake(
            activity_description=args.activity,
            expected_annual_turnover_nis=args.turnover,
            expected_monthly_profit_nis=args.profit,
            current_osek_patur_ceiling_nis=args.ceiling,
            regulated_profession=args.regulated_profession,
            clients_require_tax_invoice=args.clients_require_tax_invoice,
            foreign_clients=args.foreign_clients,
            currently_employee=args.currently_employee,
            receives_benefits=args.receives_benefits,
        )
        print(dump_json(client.classify_status(intake).to_dict()))
        return 0
    if args.command == "plan":
        print(dump_json(client.build_full_plan(load_intake(args.input)).to_dict()))
        return 0
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
