from __future__ import annotations

from common import client_from_args, parser, print_json


args = parser("Translate a support reply about a late delivery.").parse_args()
client = client_from_args(args)
job = client.create_request(
    "Sorry for the delay. A refund will be issued within 7 business days.",
    register="support",
    environment=args.env,
    audience="consumer",
)
print_json(job.to_dict())
