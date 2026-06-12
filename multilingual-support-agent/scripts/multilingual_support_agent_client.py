from __future__ import annotations

import argparse
import json
import os
from typing import Sequence

from multilingual_support_agent import Environment, SupportAgentClient, SupportContext, format_analysis


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Structured helper for multilingual Israeli support scenarios.")
    parser.add_argument("text", help="Customer message")
    parser.add_argument("--env", choices=[item.value for item in Environment], default=os.getenv("MSA_ENV", "sandbox"))
    parser.add_argument("--business-name", default=os.getenv("MSA_BUSINESS_NAME"))
    parser.add_argument("--order-id", default=os.getenv("MSA_ORDER_ID"))
    parser.add_argument("--email", default=os.getenv("MSA_EMAIL"))
    parser.add_argument("--phone", default=os.getenv("MSA_PHONE"))
    parser.add_argument("--last4", default=os.getenv("MSA_LAST4"))
    parser.add_argument("--api-key", default=os.getenv("MSA_API_KEY"), help="Accepted for integration parity; not printed.")
    return parser


def run(argv: Sequence[str] | None = None) -> dict[str, object]:
    parser = build_parser()
    args = parser.parse_args(argv)
    client = SupportAgentClient(environment=args.env, business_name=args.business_name)
    context = SupportContext(
        order_id=args.order_id,
        email=args.email,
        phone=args.phone,
        last4=args.last4,
        business_name=args.business_name,
    )
    result = client.draft_reply(args.text, context)
    return format_analysis(result)


def main(argv: Sequence[str] | None = None) -> None:
    print(json.dumps(run(argv), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
