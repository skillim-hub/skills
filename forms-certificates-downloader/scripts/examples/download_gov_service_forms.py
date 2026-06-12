#!/usr/bin/env python3
"""Search the general gov.il services source with a focused query."""
from _common import build_parser, make_client, print_json


def main() -> None:
    parser = build_parser("Discover gov.il service forms.")
    args = parser.parse_args()
    args.query = args.query or "שינוי כתובת"
    client = make_client(args)
    records = client.discover("gov-il-services", query=args.query, max_results=args.limit)
    print_json({
        "env": args.env,
        "query": args.query,
        "records": [record.to_dict() for record in records],
    })


if __name__ == "__main__":
    main()
