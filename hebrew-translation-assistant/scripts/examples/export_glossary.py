from __future__ import annotations

from common import client_from_args, parser, print_json


args = parser("Export the built-in glossary.").parse_args()
client = client_from_args(args)
print_json({"environment": args.env, "glossary": client.export_glossary()})
