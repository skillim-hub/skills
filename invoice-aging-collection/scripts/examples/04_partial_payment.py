"""Example 4: Handle a partial payment and show remaining balance."""

from _example_common import build_parser, client_mod, load_ledger, print_json

args = build_parser(__doc__).parse_args()
ledger = load_ledger(args.ledger)
ledger["invoices"][0].setdefault("partial_payments", []).append({"date": args.as_of, "amount": "250.00"})
client = client_mod.InvoiceAgingClient(ledger)
print_json({"environment": args.env, "record": client.aging_records(args.as_of)[0].to_dict()})
