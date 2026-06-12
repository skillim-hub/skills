#!/usr/bin/env python3
from _example_loader import build_client, common_parser, context_from_args, emit

parser = common_parser("Quote generation scenario")
parser.add_argument("--message", default="אני רוצה הצעת מחיר ל-CRM מקצועי")
args = parser.parse_args()
bot = build_client(args)
response = bot.recommend(args.message, context_from_args(args, {"name": "מאיה", "has_marketing_consent": True, "preferred_installments": 6, "budget_ils": "700"}))
emit({"quote_id": response.quote_id, "quote": bot.make_quote(response), "environment": args.env})
