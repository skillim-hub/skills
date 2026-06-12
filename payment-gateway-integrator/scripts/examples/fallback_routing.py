from common import FakeTransport, IsraeliPaymentOrchestrator, PaymentGatewayError, demo_gateway, demo_request, output, parse_env, response_to_dict

args = parse_env()
failure = PaymentGatewayError("timeout", code="network_timeout", retryable=True)
transport = FakeTransport(
    responses=[{"success": True, "transaction_id": "gr-fallback-1", "status": "approved"}],
    failures=[failure],
)
gateways = [demo_gateway(args.env, "cardcom", priority=1), demo_gateway(args.env, "grow", priority=2)]
orchestrator = IsraeliPaymentOrchestrator(gateways, transport=transport)
response = orchestrator.charge(demo_request(order_id="DEMO-FALLBACK-1"))

output({"environment": args.env, "gateway_used": response.gateway, "calls": len(transport.calls), "response": response_to_dict(response)})
