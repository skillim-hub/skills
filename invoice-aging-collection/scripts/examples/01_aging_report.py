"""Example 1: Generate an aging report from sample data or a ledger path."""

from _example_common import build_parser, client_mod, load_ledger, print_json

args = build_parser(__doc__).parse_args()
client = client_mod.InvoiceAgingClient(load_ledger(args.ledger))
print_json({"environment": args.env, "report": client.aging_report(args.as_of)})
