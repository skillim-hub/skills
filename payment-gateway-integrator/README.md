# Payment Gateway Integrator

Neutral skill package for integrating Cardcom, Tranzila, Pelecard, and Grow (formerly Meshulam, with legacy Meshulam contracts where applicable) behind a single Israeli payment-orchestration API.

## Install for local development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

The editable install exposes the importable package and the CLI command:

```bash
python -c "from payment_gateway_integrator import IsraeliPaymentOrchestrator; print(IsraeliPaymentOrchestrator.__name__)"
pgi-payment --help
```

## Quick start

Run tests:

```bash
pytest
```

Create an example configuration:

```bash
pgi-payment init-config --env sandbox --output config.example.json
```

Create a charge request:

```bash
cat > payment-request.json <<'JSON'
{
  "order_id": "INV-2026-0042",
  "amount": "349.90",
  "currency": "ILS",
  "description": "Consulting package",
  "customer": {
    "name": "Dana Levi",
    "email": "dana@example.co.il",
    "phone": "+972501234567"
  },
  "installments": 1,
  "return_url": "https://example.co.il/pay/return",
  "notify_url": "https://example.co.il/pay/callback"
}
JSON
```

Create a payment, extract the transaction id from the response, then use that id in the next step:

```bash
create_response="$(pgi-payment charge --config config.example.json --request payment-request.json)"
transaction_id="$(python -c 'import json,sys; data=json.load(sys.stdin); print(data.get("transaction_id") or data.get("payment_id") or "")' <<< "$create_response")"
pgi-payment status --config config.example.json --gateway grow --transaction-id "$transaction_id"
```

Use the typed client directly:

```python
from payment_gateway_integrator import (
    Customer,
    GatewayConfig,
    IsraeliPaymentOrchestrator,
    PaymentRequest,
)

gateway = GatewayConfig(
    name="grow",
    endpoint_url="https://sandbox.example/grow",
    api_key="replace-in-secret-manager",
    terminal_id="replace-terminal-id",
    secret="replace-callback-secret",
    capabilities={"hosted_checkout", "refund", "installments"},
    max_installments=12,
)

payment = PaymentRequest(
    order_id="INV-2026-0042",
    amount_agorot=34990,
    currency="ILS",
    description="Consulting package",
    customer=Customer(name="Dana Levi", email="dana@example.co.il", phone="+972501234567"),
    installments=1,
    return_url="https://example.co.il/pay/return",
    notify_url="https://example.co.il/pay/callback",
)

orchestrator = IsraeliPaymentOrchestrator([gateway])
create_response = orchestrator.charge(payment)
transaction_id = create_response.transaction_id or str(create_response.raw.get("payment_id", ""))
status_response = orchestrator.status(create_response.gateway, transaction_id)
```


## Web-validated source posture

The v3 pass validates live official or provider sources for VAT, Cardcom, Tranzila, Grow, Pelecard, SHVA/Ashrait, Bank of Israel payment-system context, privacy, consumer-price display, and PCI storage rules. Read `references/verification-log.md` before changing provider-specific fields.

## Examples

Each script accepts `--env sandbox|production`, reads environment variables, and prints JSON with `ensure_ascii=False` and `indent=2`.

```bash
export PGI_GATEWAY=grow
export PGI_API_KEY=replace-in-secret-manager
export PGI_TERMINAL_ID=replace-terminal-id
export PGI_SECRET=replace-callback-secret
python scripts/examples/one_time_charge.py --env sandbox
python scripts/examples/hosted_checkout.py --env sandbox
python scripts/examples/fallback_routing.py --env sandbox
python scripts/examples/refund_flow.py --env sandbox
python scripts/examples/webhook_verify.py --env sandbox
python scripts/examples/async_charge.py --env sandbox
```

Optional environment variables:

| Variable | Purpose |
|---|---|
| `PGI_GATEWAY` | Gateway name, default `grow`. |
| `PGI_ENDPOINT_URL_SANDBOX` | Sandbox endpoint override. |
| `PGI_ENDPOINT_URL_PRODUCTION` | Production endpoint override. |
| `PGI_ENDPOINT_URL` | Fallback endpoint override. |
| `PGI_API_KEY` | Provider API key. |
| `PGI_TERMINAL_ID` | Terminal or merchant identifier. |
| `PGI_SECRET` | Callback signing secret. |
| `PGI_RETURN_URL` | Customer return URL. |
| `PGI_NOTIFY_URL` | Server callback URL. |
| `PGI_CUSTOMER_EMAIL` | Example customer email. |

## File index

| File | Purpose |
|---|---|
| `SKILL.md` | English implementation guide. |
| `SKILL_HE.md` | Hebrew implementation guide with Israeli terminology. |
| `references/api-reference.md` | Canonical API, provider mapping, regulation references, error tables. |
| `references/workflow-guide.md` | End-to-end workflows. |
| `references/troubleshooting.md` | Production troubleshooting playbooks. |
| `references/test-scenarios.md` | Concrete test scenarios. |
| `references/migration-checklist.md` | Gateway migration and cutover checklist. |
| `references/gateway-matrix.md` | Capability matrix and merchant recommendations. |
| `references/branding-audit.md` | Neutrality and public Markdown audit summary. |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization correction log. |
| `src/payment_gateway_integrator/` | Importable package. |
| `scripts/payment_gateway_integrator_client.py` | Compatibility entry point for client imports. |
| `scripts/payment_gateway_integrator_cli.py` | Compatibility entry point for CLI execution. |
| `scripts/test_payment_gateway_integrator_client.py` | Pytest suite with more than 20 tests. |
| `scripts/examples/` | Runnable scenario examples using safe fake transports by default. |
| `metadata.json` | Skill metadata without author field. |
| `CHANGELOG.md` | Keep a Changelog format. |
| `LICENSE` | MIT license. |
| `pyproject.toml` | Packaging and test configuration. |
| `requirements-dev.txt` | Development dependencies. |

## Production notes

- Use real provider credentials only through environment variables or a secret manager.
- Validate endpoint paths and field names against the active merchant portal.
- Do not store full card numbers or CVV.
- Verify callbacks from raw body bytes.
- Reconcile daily in `Asia/Jerusalem`.
- Display amounts as `₪123.45` and local dates as `DD/MM/YYYY`.
