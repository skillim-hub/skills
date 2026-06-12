#!/usr/bin/env python3
from _example_loader import build_client, common_parser, context_from_args, emit

parser = common_parser("Budget-sensitive upsell scenario")
parser.add_argument("--message", default="צריך CRM אבל התקציב שלי עד 300 שקל")
args = parser.parse_args()
bot = build_client(args)
response = bot.recommend(args.message, context_from_args(args, {"name": "יובל", "has_marketing_consent": True, "budget_ils": "300"}))
emit(response.to_dict())
