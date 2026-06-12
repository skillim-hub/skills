import asyncio

from common import AsyncFakeTransport, AsyncIsraeliPaymentOrchestrator, demo_gateway, demo_request, output, parse_env, response_to_dict


async def main() -> None:
    args = parse_env()
    transport = AsyncFakeTransport([
        {"success": True, "transaction_id": "async-demo-1", "status": "approved"}
    ])
    orchestrator = AsyncIsraeliPaymentOrchestrator([demo_gateway(args.env, args.gateway)], transport=transport)
    response = await orchestrator.charge(demo_request(order_id="DEMO-ASYNC-1"))
    output({"environment": args.env, "response": response_to_dict(response), "calls": len(transport.calls)})


if __name__ == "__main__":
    asyncio.run(main())
