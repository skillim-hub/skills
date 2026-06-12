#!/usr/bin/env python3
"""Structured helper entrypoint for the Hebrew Email Formatter package."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from hebrew_email_formatter import (
    Contact,
    DraftStore,
    EmailRequest,
    HebrewEmailError,
    HebrewEmailFormatterClient,
    Sender,
    format_date_il,
    format_ils,
    parse_environment,
    parse_formality,
    parse_gender,
    parse_purpose,
)


def build_request(args: argparse.Namespace) -> EmailRequest:
    facts = {
        key: value
        for key, value in {
            "invoice_number": args.invoice_number,
            "invoice_date": args.invoice_date,
            "due_date": args.due_date,
            "amount": args.amount,
            "payment_terms": args.payment_terms,
            "service": args.service,
            "topic": args.topic,
            "valid_until": args.valid_until,
            "vat_status": args.vat_status,
            "requested_action_date": args.requested_action_date,
        }.items()
        if value
    }
    return EmailRequest(
        purpose=parse_purpose(args.purpose),
        formality=parse_formality(args.formality),
        recipient=Contact(name=args.recipient or "", gender=parse_gender(args.recipient_gender)),
        sender=Sender(name=args.sender or "", gender=parse_gender(args.sender_gender), phone=args.phone or "", email=args.email or ""),
        facts=facts,
        environment=parse_environment(args.env),
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Format professional Hebrew email drafts.")
    sub = parser.add_subparsers(dest="command", required=True)

    amount_cmd = sub.add_parser("amount")
    amount_cmd.add_argument("value")
    amount_cmd.add_argument("--agorot", action="store_true")

    date_cmd = sub.add_parser("date")
    date_cmd.add_argument("value")

    create_cmd = sub.add_parser("create")
    create_cmd.add_argument("--purpose", required=True)
    create_cmd.add_argument("--formality", default="neutral")
    create_cmd.add_argument("--recipient", default="")
    create_cmd.add_argument("--recipient-gender", default="neutral")
    create_cmd.add_argument("--sender", default="")
    create_cmd.add_argument("--sender-gender", default="neutral")
    create_cmd.add_argument("--phone", default="")
    create_cmd.add_argument("--email", default="")
    create_cmd.add_argument("--amount", default="")
    create_cmd.add_argument("--invoice-number", default="")
    create_cmd.add_argument("--invoice-date", default="")
    create_cmd.add_argument("--due-date", default="")
    create_cmd.add_argument("--payment-terms", default="")
    create_cmd.add_argument("--service", default="")
    create_cmd.add_argument("--topic", default="")
    create_cmd.add_argument("--valid-until", default="")
    create_cmd.add_argument("--vat-status", default="")
    create_cmd.add_argument("--requested-action-date", default="")
    create_cmd.add_argument("--env", choices=["sandbox", "production"], default="sandbox")
    create_cmd.add_argument("--save", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.command == "amount":
            print(format_ils(args.value, include_agorot=args.agorot))
            return 0
        if args.command == "date":
            print(format_date_il(args.value))
            return 0
        request = build_request(args)
        draft = HebrewEmailFormatterClient().compose(request)
        if args.save:
            DraftStore().save(draft)
        print(json.dumps(draft.to_dict(), ensure_ascii=False, indent=2))
        return 0
    except HebrewEmailError as exc:
        print(f"שגיאה: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
