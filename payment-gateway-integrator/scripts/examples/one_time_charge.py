from common import FakeTransport, IsraeliPaymentOrchestrator, demo_gateway, demo_request, output, parse_env, response_to_dict

args = parse_env()
transport = FakeTransport([
    {"success": True, "transaction_id": "gr-demo-1", "status": "approved", "approval_code": "123456"}
])
orchestrator = IsraeliPaymentOrchestrator([demo_gateway(args.env, args.gateway)], transport=transport)
response = orchestrator.charge(demo_request(order_id="DEMO-CHARGE-1"))

output({"environment": args.env, "response": response_to_dict(response), "calls": len(transport.calls)})
