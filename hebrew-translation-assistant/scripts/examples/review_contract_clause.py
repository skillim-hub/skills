from __future__ import annotations

from common import client_from_args, parser, print_json


args = parser("Review a lease clause with legal-sensitive terminology.").parse_args()
client = client_from_args(args)
review = client.review_text(
    "הסכם שכירות זה כולל שטר חוב וייפוי כוח.",
    direction="he-to-en",
    register="legal",
)
print_json(review)
