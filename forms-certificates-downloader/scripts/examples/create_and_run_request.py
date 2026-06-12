#!/usr/bin/env python3
"""Create a saved request, extract its id, then run it."""
from _common import build_parser, make_client, print_json


def main() -> None:
    parser = build_parser("Create and run a saved request.")
    args = parser.parse_args()
    args.query = args.query or "1301"
    client = make_client(args)
    request = client.create_download_request("tax-authority-public-forms", query=args.query, limit=args.limit, env=args.env)
    result = client.run_download_request(request.request_id)
    print_json({
        "create_response": request.to_dict(),
        "extracted_request_id": request.request_id,
        "run_response": result,
    })


if __name__ == "__main__":
    main()
