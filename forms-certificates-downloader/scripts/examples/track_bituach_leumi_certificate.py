#!/usr/bin/env python3
"""Track public National Insurance documents for a benefit-related query."""
from _common import build_parser, make_client, print_json


def main() -> None:
    parser = build_parser("Track public National Insurance documents.")
    args = parser.parse_args()
    args.query = args.query or "אישור שנתי"
    client = make_client(args)
    records, changes = client.refresh_source("bituach-leumi-certificates", query=args.query, max_results=args.limit)
    print_json({
        "env": args.env,
        "query": args.query,
        "records": [record.to_dict() for record in records],
        "changes": [change.to_dict() for change in changes],
    })


if __name__ == "__main__":
    main()
