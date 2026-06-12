#!/usr/bin/env python3
"""Discover and download public Tax Authority forms matching a query."""
from _common import build_parser, make_client, print_json


def main() -> None:
    parser = build_parser("Download public Tax Authority forms.")
    args = parser.parse_args()
    args.query = args.query or "1301"
    client = make_client(args)
    records = client.discover("tax-authority-public-forms", query=args.query, max_results=args.limit)
    downloaded = [client.download(record) for record in records]
    changes = client.track_records(downloaded)
    print_json({
        "env": args.env,
        "query": args.query,
        "downloaded": [record.to_dict() for record in downloaded],
        "changes": [change.to_dict() for change in changes],
    })


if __name__ == "__main__":
    main()
