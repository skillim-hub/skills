#!/usr/bin/env python3
"""Print configured registry sources as JSON."""
from _common import build_parser, make_client, print_json


def main() -> None:
    parser = build_parser("Print configured registry sources.")
    args = parser.parse_args()
    client = make_client(args)
    print_json([source.to_dict() for source in client.list_sources()])


if __name__ == "__main__":
    main()
