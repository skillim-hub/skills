#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from customer_service_chat_agent import CustomerContext, CustomerServiceChatAgent, Environment, response_to_dict, ticket_to_dict


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("CHAT_AGENT_ENV", "sandbox"))
    return parser.parse_args()


def environment(value: str) -> Environment:
    return Environment.PRODUCTION if value == "production" else Environment.SANDBOX


def main():
    args = parse_args()
    env = environment(args.env)
    agent = CustomerServiceChatAgent()
    context = CustomerContext(
        name=os.getenv("CUSTOMER_NAME"),
        contact=os.getenv("CUSTOMER_CONTACT"),
        order_number=os.getenv("ORDER_NUMBER"),
        channel=os.getenv("CHAT_CHANNEL", "chat"),
    )
    response = agent.reply(os.getenv("CUSTOMER_MESSAGE", "צריך חשבונית לחברה על הזמנה 10493"), context)
    payload = response_to_dict(response)
    payload["environment"] = env.value
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
