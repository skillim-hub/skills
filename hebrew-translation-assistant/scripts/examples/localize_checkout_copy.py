from __future__ import annotations

from common import client_from_args, parser, print_json


args = parser("Localize e-commerce checkout copy.").parse_args()
client = client_from_args(args)
result = client.translate_text(
    "Add to cart, checkout, order summary, coupon code, payment method.",
    direction="en-to-he",
    register="business",
    audience="online shoppers",
)
print_json(result.to_dict())
