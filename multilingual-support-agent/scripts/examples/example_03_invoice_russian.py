from __future__ import annotations

import argparse
import json
import os

from multilingual_support_agent import SupportAgentClient, SupportContext, format_analysis


DEFAULT_TEXT = 'Я не получил чек по заказу'


def main() -> None:
    parser = argparse.ArgumentParser(description='Russian accounting document scenario')
    parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("MSA_ENV", "sandbox"))
    parser.add_argument("--text", default=os.getenv('MSA_EXAMPLE_TEXT', DEFAULT_TEXT))
    parser.add_argument("--business-name", default=os.getenv("MSA_BUSINESS_NAME"))
    parser.add_argument("--order-id", default=os.getenv("MSA_ORDER_ID"))
    parser.add_argument("--email", default=os.getenv("MSA_EMAIL"))
    parser.add_argument("--phone", default=os.getenv("MSA_PHONE"))
    parser.add_argument("--last4", default=os.getenv("MSA_LAST4"))
    parser.add_argument("--api-key", default=os.getenv("MSA_API_KEY"), help="Accepted for integration parity; not printed.")
    args = parser.parse_args()

    client = SupportAgentClient(environment=args.env, business_name=args.business_name)
    context = SupportContext(
        order_id=args.order_id,
        email=args.email,
        phone=args.phone,
        last4=args.last4,
        business_name=args.business_name,
    )
    result = client.draft_reply(args.text, context)
    print(json.dumps(format_analysis(result), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
