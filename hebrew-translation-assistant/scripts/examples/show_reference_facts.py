from __future__ import annotations

from common import client_from_args, parser, print_json


args = parser("Show source-sensitive Israeli reference facts for this release.").parse_args()
client = client_from_args(args)
print_json({"environment": args.env, "facts": client.reference_facts()})
