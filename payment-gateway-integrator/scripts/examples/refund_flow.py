from common import FakeTransport, IsraeliPaymentOrchestrator, RefundRequest, demo_gateway, output, parse_env, response_to_dict

args = parse_env()
transport = FakeTransport([
    {"success": True, "refund_id": "rf-demo-1", "status": "approved"}
])
orchestrator = IsraeliPaymentOrchestrator([demo_gateway(args.env, args.gateway)], transport=transport)
refund = RefundRequest(transaction_id="gr-demo-1", amount_agorot=5000, reason="Partial refund")
response = orchestrator.refund(args.gateway, refund)

output({"environment": args.env, "response": response_to_dict(response)})
