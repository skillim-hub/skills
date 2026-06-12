"""Example 2: Render a friendly WhatsApp reminder."""

from _example_common import build_parser, client_mod, load_ledger, print_json

args = build_parser(__doc__).parse_args()
client = client_mod.InvoiceAgingClient(load_ledger(args.ledger))
reminder = client.render_for_invoice(args.invoice_id, "friendly_whatsapp", args.as_of)
print_json({"environment": args.env, "reminder": reminder.to_payload()})
