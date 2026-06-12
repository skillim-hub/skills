#!/usr/bin/env python3
"""Export an existing manifest to CSV and print the output path."""
from pathlib import Path

from _common import build_parser, make_client, print_json


def main() -> None:
    parser = build_parser("Export manifest CSV.")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    client = make_client(args)
    output = Path(args.output) if args.output else Path(args.download_dir) / "forms-register.csv"
    path = client.export_manifest_csv(output)
    print_json({"env": args.env, "csv_path": str(path)})


if __name__ == "__main__":
    main()
