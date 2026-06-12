from __future__ import annotations

from common import client_from_args, parser, print_json


args = parser("Translate an invoice email for an Israeli freelancer.").parse_args()
client = client_from_args(args)
job = client.create_request(
    "Please issue a tax invoice/receipt for ₪1,250 plus VAT by 2026-03-05.",
    register="accounting",
    environment=args.env,
    audience="freelance client",
)
print_json(job.to_dict())
