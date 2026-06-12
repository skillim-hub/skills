from common import FakeTransport, IsraeliPaymentOrchestrator, demo_gateway, demo_request, output, parse_env, response_to_dict

args = parse_env()
transport = FakeTransport([
    {"success": True, "payment_id": "gr-page-1", "checkout_url": "https://pay.example/checkout/gr-page-1", "status": "pending"}
])
orchestrator = IsraeliPaymentOrchestrator([demo_gateway(args.env, args.gateway)], transport=transport)
response = orchestrator.charge(demo_request(order_id="DEMO-CHECKOUT-1", installments=3, tokenize=True))

output({"environment": args.env, "redirect_url": response.redirect_url, "response": response_to_dict(response)})
