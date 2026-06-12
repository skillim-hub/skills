#!/usr/bin/env python3
"""Compatibility entry point for the installable package client."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Sequence
from multi_line_item_aggregator import CalculationOptions, DiscountAllocationMethod, aggregate_invoice, create_sample_invoice, format_summary, load_lines_from_csv, load_lines_from_json, parse_discount, save_result_json

def build_arg_parser() -> argparse.ArgumentParser:
    """Build the argparse interface."""
    parser=argparse.ArgumentParser(description='Aggregate multi-line invoices with discounts and per-line VAT')
    sub=parser.add_subparsers(dest='command')
    sample=sub.add_parser('create-sample'); sample.add_argument('output_file'); sample.add_argument('--env', choices=['sandbox','production'], default='sandbox')
    agg=sub.add_parser('aggregate'); agg.add_argument('input'); agg.add_argument('--format', choices=['json','csv'], default=None); agg.add_argument('--id', dest='invoice_id', default=''); agg.add_argument('--invoice-id', dest='invoice_id_alias', default=''); agg.add_argument('--invoice-date', default=''); agg.add_argument('--vat-number', default=''); agg.add_argument('--invoice-discount-type', choices=['amount','percent'], default=None); agg.add_argument('--invoice-discount-value', default=None); agg.add_argument('--allocation', choices=['by_net','by_gross','equal'], default='by_net'); agg.add_argument('--env', choices=['sandbox','production'], default='sandbox'); agg.add_argument('--output','-o', default=''); agg.add_argument('--json', action='store_true')
    return parser

def main(argv: Sequence[str] | None = None) -> int:
    """Run the argparse command-line interface."""
    parser=build_arg_parser(); args=parser.parse_args(argv)
    if args.command=='create-sample': print(json.dumps(create_sample_invoice(args.output_file, environment=args.env), ensure_ascii=False, indent=2)); return 0
    if args.command!='aggregate': parser.print_help(); return 2
    path=Path(args.input); fmt=args.format or path.suffix.lower().lstrip('.')
    lines=load_lines_from_json(path) if fmt=='json' else load_lines_from_csv(path) if fmt=='csv' else None
    if lines is None: parser.error('Input format must be JSON or CSV')
    result=aggregate_invoice(lines, invoice_id=args.invoice_id or args.invoice_id_alias, invoice_date=args.invoice_date, vat_number=args.vat_number, invoice_discount=parse_discount(args.invoice_discount_type, args.invoice_discount_value), options=CalculationOptions(invoice_discount_allocation=DiscountAllocationMethod(args.allocation), environment=args.env))
    if args.output: save_result_json(result, args.output)
    print(result.to_json() if args.json else format_summary(result)); return 0
if __name__ == '__main__': raise SystemExit(main())
