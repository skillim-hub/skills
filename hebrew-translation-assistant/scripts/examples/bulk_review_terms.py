from __future__ import annotations

from common import client_from_args, parser, print_json


args = parser("Review several business terms.").parse_args()
client = client_from_args(args)
terms = ["חשבונית מס", "ניכוי מס במקור", "מדיניות פרטיות", "איסוף עצמי", "דמי ביטול"]
payload = {term: client.glossary_lookup(term) for term in terms}
print_json({"environment": args.env, "terms": payload})
