"""Example 5: Build an evidence checklist for a client."""

from _example_common import build_parser, client_mod, load_ledger, print_json

args = build_parser(__doc__).parse_args()
client = client_mod.InvoiceAgingClient(load_ledger(args.ledger))
print_json({"environment": args.env, "evidence_pack": client.evidence_pack(args.client_id, args.as_of)})
