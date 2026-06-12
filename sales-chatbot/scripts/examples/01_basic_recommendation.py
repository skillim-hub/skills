#!/usr/bin/env python3
from _example_loader import build_client, common_parser, context_from_args, emit

parser = common_parser("Basic recommendation scenario")
parser.add_argument("--message", default="שלום, כמה עולה CRM לעסק קטן?")
args = parser.parse_args()
bot = build_client(args)
response = bot.recommend(args.message, context_from_args(args, {"name": "דנה", "has_marketing_consent": True, "preferred_installments": 3}))
emit(response.to_dict())
