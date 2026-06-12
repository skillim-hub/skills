#!/usr/bin/env python3
"""Command-line helper for the Corporate-Law Guide."""

from __future__ import annotations

import argparse
import json
from typing import Any, Optional

from . import CorporateLawGuideClient


def _yes(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    lowered = value.strip().lower()
    if lowered in {"yes", "y", "true", "1", "כן"}:
        return True
    if lowered in {"no", "n", "false", "0", "לא"}:
        return False
    raise argparse.ArgumentTypeError("Expected yes/no")


def _print_result(result: Any, output: str = "json") -> None:
    client = CorporateLawGuideClient()
    if output == "markdown" and hasattr(result, "to_markdown"):
        print(result.to_markdown())
    elif hasattr(result, "to_json"):
        print(result.to_json())
    else:
        print(client.render_json(result))


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Corporate-Law Guide CLI")
    parser.add_argument("--env", choices=["sandbox", "production"], default="sandbox", help="Execution environment label")
    sub = parser.add_subparsers(dest="command", required=True)

    facts = sub.add_parser("facts", help="Print dated regulatory facts validated in the package")
    facts.add_argument("--output", choices=["json"], default="json")

    create_case = sub.add_parser("create-case", help="Create a case response that includes case_id")
    create_case.add_argument("--owners", type=int, required=True)
    create_case.add_argument("--activity", required=True)
    create_case.add_argument("--company-number")
    create_case.add_argument("--note", action="append", default=[])

    case_checklist = sub.add_parser("case-checklist", help="Create a checklist using a case_id from create-case")
    case_checklist.add_argument("--case-id", required=True)
    case_checklist.add_argument("--action", choices=["incorporation", "annual_report", "share_transfer", "director_change", "shareholder_agreement", "due_diligence", "dormant_cleanup"], required=True)
    case_checklist.add_argument("--owners", type=int, default=1)
    case_checklist.add_argument("--activity", default="business activity")
    case_checklist.add_argument("--company-number")
    case_checklist.add_argument("--year", type=int, default=2026)
    case_checklist.add_argument("--output", choices=["json", "markdown"], default="json")

    classify = sub.add_parser("classify", help="Classify entity structure to investigate")
    classify.add_argument("--owners", type=int, required=True)
    classify.add_argument("--liability-risk", choices=["low", "medium", "high"], default="medium")
    classify.add_argument("--fundraising", type=_yes, default=False)
    classify.add_argument("--regulated", type=_yes, default=False)
    classify.add_argument("--non-profit", type=_yes, default=False)
    classify.add_argument("--activity", required=True)
    classify.add_argument("--output", choices=["json"], default="json")

    annual = sub.add_parser("annual-report", help="Create annual-report checklist")
    annual.add_argument("--company-number", required=True)
    annual.add_argument("--year", type=int, required=True)
    annual.add_argument("--has-changes", type=_yes, default=False)
    annual.add_argument("--output", choices=["json", "markdown"], default="json")

    shareholder = sub.add_parser("shareholder-scan", help="Scan shareholder agreement issues")
    shareholder.add_argument("--founders", type=int, required=True)
    shareholder.add_argument("--equal-holdings", type=_yes, default=False)
    shareholder.add_argument("--investor-round", type=_yes, default=False)
    shareholder.add_argument("--family-company", type=_yes, default=False)
    shareholder.add_argument("--output", choices=["json", "markdown"], default="json")

    validate = sub.add_parser("validate-company-number", help="Validate company-number format")
    validate.add_argument("company_number")

    checklist = sub.add_parser("checklist", help="Create workflow checklist")
    checklist.add_argument("action", choices=["incorporation", "director-change", "share-transfer", "due-diligence", "dormant-cleanup"])
    checklist.add_argument("--owners", type=int, default=1)
    checklist.add_argument("--activity", default="business activity")
    checklist.add_argument("--regulated", type=_yes, default=False)
    checklist.add_argument("--foreign-shareholders", type=_yes, default=False)
    checklist.add_argument("--director-action", choices=["appoint", "resign", "remove"], default="appoint")
    checklist.add_argument("--bank-signing-change", type=_yes, default=False)
    checklist.add_argument("--seller-shares", type=int, default=100)
    checklist.add_argument("--transfer-quantity", type=int, default=10)
    checklist.add_argument("--family-transfer", type=_yes, default=False)
    checklist.add_argument("--new-shareholder", type=_yes, default=False)
    checklist.add_argument("--tax-review-done", type=_yes, default=False)
    checklist.add_argument("--output", choices=["json", "markdown"], default="json")

    args = parser.parse_args(argv)
    client = CorporateLawGuideClient(environment=args.env)

    if args.command == "facts":
        print(json.dumps(client.regulatory_facts_payload(), ensure_ascii=False, indent=2))
    elif args.command == "create-case":
        result = client.create_case(args.activity, args.owners, company_number=args.company_number, notes=args.note, environment=args.env)
        _print_result(result)
    elif args.command == "case-checklist":
        if args.action == "incorporation":
            result = client.build_incorporation_checklist(args.owners, args.activity, case_id=args.case_id)
        elif args.action == "annual_report":
            if not args.company_number:
                raise SystemExit("--company-number is required for annual_report")
            result = client.annual_report_checklist(args.company_number, args.year, case_id=args.case_id)
        elif args.action == "share_transfer":
            result = client.share_transfer_checklist(100, 10, case_id=args.case_id)
        elif args.action == "director_change":
            result = client.director_change_checklist("appoint", case_id=args.case_id)
        elif args.action == "shareholder_agreement":
            result = client.shareholder_agreement_scan(args.owners, case_id=args.case_id)
        elif args.action == "due_diligence":
            result = client.due_diligence_checklist(case_id=args.case_id)
        else:
            result = client.dormant_cleanup_checklist(case_id=args.case_id)
        _print_result(result, args.output)
    elif args.command == "classify":
        result = client.classify_entity_need(
            business_activity=args.activity,
            owners_count=args.owners,
            liability_risk=args.liability_risk,
            fundraising_plan=args.fundraising,
            regulated_activity=args.regulated,
            non_profit_purpose=args.non_profit,
        )
        _print_result(result, args.output)
    elif args.command == "annual-report":
        result = client.annual_report_checklist(args.company_number, args.year, args.has_changes)
        _print_result(result, args.output)
    elif args.command == "shareholder-scan":
        result = client.shareholder_agreement_scan(
            founders_count=args.founders,
            equal_holdings=args.equal_holdings,
            investor_round=args.investor_round,
            family_company=args.family_company,
        )
        _print_result(result, args.output)
    elif args.command == "validate-company-number":
        result = client.validate_company_number(args.company_number)
        _print_result(result)
    elif args.command == "checklist":
        if args.action == "incorporation":
            result = client.build_incorporation_checklist(args.owners, args.activity, args.regulated, args.foreign_shareholders)
        elif args.action == "director-change":
            result = client.director_change_checklist(args.director_action, args.bank_signing_change)
        elif args.action == "share-transfer":
            result = client.share_transfer_checklist(
                args.seller_shares,
                args.transfer_quantity,
                args.family_transfer,
                args.new_shareholder,
                args.tax_review_done,
            )
        elif args.action == "due-diligence":
            result = client.due_diligence_checklist()
        else:
            result = client.dormant_cleanup_checklist()
        _print_result(result, args.output)


if __name__ == "__main__":
    main()

