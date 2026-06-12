"""Example 7: Create an invoice record and append it to a sample ledger in memory."""

from _example_common import build_parser, client_mod, load_ledger, print_json

args = build_parser(__doc__).parse_args()
ledger = load_ledger(args.ledger)
record = client_mod.create_invoice_record(
    client_id=args.client_id,
    issue_date=args.as_of,
    amount="1800.00",
    due_date=args.as_of,
    existing_invoice_ids=[invoice["invoice_id"] for invoice in ledger.get("invoices", [])],
)
ledger.setdefault("invoices", []).append(record)
print_json({"environment": args.env, "created": record, "invoice_count": len(ledger["invoices"])})
