"""Example 6: Async dry-run dispatch."""

import asyncio

from _example_common import build_parser, client_mod, load_ledger, print_json


async def main() -> None:
    args = build_parser(__doc__).parse_args()
    client = client_mod.InvoiceAgingClient(load_ledger(args.ledger))
    results = await client.async_send_due(args.as_of, channel="whatsapp", dry_run=True)
    print_json({"environment": args.env, "results": results})


asyncio.run(main())
