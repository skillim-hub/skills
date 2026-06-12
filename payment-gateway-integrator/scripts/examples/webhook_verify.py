from common import IsraeliPaymentOrchestrator, demo_gateway, output, parse_env

args = parse_env()
orchestrator = IsraeliPaymentOrchestrator([demo_gateway(args.env, args.gateway)])
payload = b'{"order_id":"DEMO-0001","status":"approved"}'
signature = orchestrator.sign_webhook_payload(args.gateway, payload)

output({
    "environment": args.env,
    "signature": signature,
    "valid": orchestrator.verify_webhook(args.gateway, payload, signature),
    "tampered_valid": orchestrator.verify_webhook(args.gateway, b"{}", signature),
})
