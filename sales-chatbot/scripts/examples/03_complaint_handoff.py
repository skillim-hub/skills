#!/usr/bin/env python3
from _example_loader import build_client, common_parser, context_from_args, emit

parser = common_parser("Complaint handoff scenario")
parser.add_argument("--message", default="המוצר לא עובד ואני מאוכזבת")
args = parser.parse_args()
bot = build_client(args)
response = bot.recommend(args.message, context_from_args(args, {"name": "נועה"}))
emit(response.to_dict())
