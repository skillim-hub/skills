#!/usr/bin/env python3
import asyncio
from _example_loader import build_client, common_parser, context_from_args, emit

parser = common_parser("Async webhook-style scenario")
parser.add_argument("--message", default="אפשר לקבל הצעה כולל תשלומים?")
args = parser.parse_args()

async def main():
    bot = build_client(args)
    response = await bot.recommend_async(args.message, context_from_args(args, {"name": "אורי", "has_marketing_consent": True, "preferred_installments": 6}))
    emit(response.to_dict())

asyncio.run(main())
