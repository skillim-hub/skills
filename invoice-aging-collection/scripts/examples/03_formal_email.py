"""Example 3: Render a formal email for human review."""

from _example_common import build_parser, client_mod, load_ledger, print_json

args = build_parser(__doc__).parse_args()
client = client_mod.InvoiceAgingClient(load_ledger(args.ledger))
reminder = client.render_for_invoice(args.invoice_id, "formal_email", args.as_of)
print_json(
    {
        "environment": args.env,
        "subject": reminder.subject,
        "body": reminder.body,
        "requires_human_review": reminder.requires_human_review,
    }
)
