from __future__ import annotations

import pytest

import payment_gateway_integrator as pgi


class FakeTransport:
    def __init__(self, responses=None, failures=None):
        self.responses = list(responses or [])
        self.failures = list(failures or [])
        self.calls = []

    def __call__(self, method, url, *, headers, json_body, timeout):
        self.calls.append({"method": method, "url": url, "headers": headers, "json_body": json_body, "timeout": timeout})
        if self.failures:
            raise self.failures.pop(0)
        if self.responses:
            return self.responses.pop(0)
        return {"success": True, "transaction_id": "tx-default", "status": "approved"}


class AsyncFakeTransport(FakeTransport):
    async def __call__(self, method, url, *, headers, json_body, timeout):
        return super().__call__(method, url, headers=headers, json_body=json_body, timeout=timeout)


def gateway(name="cardcom", **overrides):
    data = {
        "name": name,
        "endpoint_url": f"https://example.test/{name}",
        "api_key": "key",
        "terminal_id": "terminal",
        "secret": "secret",
        "capabilities": {"hosted_checkout", "refund", "partial_refund", "installments", "tokenization", "token_charge", "authorize", "capture"},
        "max_installments": 12,
        "priority": 10,
        "supported_currencies": {"ILS"},
    }
    data.update(overrides)
    return pgi.GatewayConfig(**data)


def request(**overrides):
    data = {
        "order_id": "INV-1",
        "amount_agorot": 34990,
        "currency": "ILS",
        "description": "בדיקה",
        "customer": pgi.Customer(name="דנה לוי", email="dana@example.co.il", phone="+972501234567"),
        "installments": 1,
        "capture": True,
        "return_url": "https://example.co.il/return",
        "notify_url": "https://example.co.il/webhook",
    }
    data.update(overrides)
    return pgi.PaymentRequest(**data)


def test_nis_to_agorot_accepts_two_decimals():
    assert pgi.nis_to_agorot("10.25") == 1025


def test_nis_to_agorot_rejects_precision():
    with pytest.raises(pgi.PaymentGatewayError) as err:
        pgi.nis_to_agorot("10.255")
    assert err.value.code == "amount_precision_invalid"


def test_format_ils():
    assert pgi.format_ils(12345) == "₪123.45"


def test_gateway_alias_normalization():
    assert pgi.normalize_gateway_name("pele-card") == "pelecard"


def test_unsupported_gateway_raises():
    with pytest.raises(pgi.PaymentGatewayError):
        pgi.normalize_gateway_name("missing")


def test_payment_request_requires_order_id():
    with pytest.raises(pgi.PaymentGatewayError) as err:
        request(order_id="").validate()
    assert err.value.code == "order_id_required"


def test_payment_request_requires_positive_amount():
    with pytest.raises(pgi.PaymentGatewayError) as err:
        request(amount_agorot=0).validate()
    assert err.value.code == "amount_invalid"


def test_choose_gateways_filters_disabled():
    orch = pgi.IsraeliPaymentOrchestrator([gateway(enabled=False), gateway("grow", priority=20)])
    chosen = orch.choose_gateways(request())
    assert [item.normalized_name() for item in chosen] == ["grow"]


def test_choose_gateways_filters_installments():
    orch = pgi.IsraeliPaymentOrchestrator([gateway("cardcom", max_installments=1, priority=10), gateway("tranzila", max_installments=12, priority=20)])
    chosen = orch.choose_gateways(request(installments=3))
    assert [item.normalized_name() for item in chosen] == ["tranzila"]


def test_choose_gateways_filters_currency():
    orch = pgi.IsraeliPaymentOrchestrator([gateway("cardcom", supported_currencies={"USD"}), gateway("grow", priority=20)])
    assert orch.choose_gateways(request())[0].normalized_name() == "grow"


def test_cardcom_payload_contains_installments():
    cfg = gateway("cardcom")
    orch = pgi.IsraeliPaymentOrchestrator([cfg])
    payload = orch.build_payment_payload(cfg, request(installments=3, tokenize=True))
    assert payload["NumOfPayments"] == 3
    assert payload["CreateToken"] is True
    assert payload["Amount"] == "349.90"


def test_tranzila_payload_contains_terminal_and_sum():
    cfg = gateway("tranzila")
    orch = pgi.IsraeliPaymentOrchestrator([cfg])
    payload = orch.build_payment_payload(cfg, request(installments=2))
    assert payload["terminal_name"] == "terminal"
    assert payload["sum"] == "349.90"
    assert payload["npay"] == 2


def test_meshulam_payload_contains_hebrew_text():
    cfg = gateway("meshulam")
    orch = pgi.IsraeliPaymentOrchestrator([cfg])
    payload = orch.build_payment_payload(cfg, request(description="בדיקת חיוב"))
    assert payload["description"] == "בדיקת חיוב"
    assert payload["fullName"] == "דנה לוי"


def test_pelecard_payload_uses_agorot_total():
    cfg = gateway("pelecard")
    orch = pgi.IsraeliPaymentOrchestrator([cfg])
    payload = orch.build_payment_payload(cfg, request())
    assert payload["Total"] == "34990"


def test_grow_payload_contains_customer_object():
    cfg = gateway("grow")
    orch = pgi.IsraeliPaymentOrchestrator([cfg])
    payload = orch.build_payment_payload(cfg, request())
    assert payload["customer"]["email"] == "dana@example.co.il"


def test_parse_approved_response():
    orch = pgi.IsraeliPaymentOrchestrator([gateway()])
    response = orch.parse_payment_response(gateway(), request(), {"ResponseCode": 0, "LowProfileId": "lp1", "authnr": "123456"})
    assert response.status == pgi.PaymentStatus.APPROVED
    assert response.transaction_id == "lp1"
    assert response.approval_code == "123456"


def test_parse_redirect_response_requires_action():
    orch = pgi.IsraeliPaymentOrchestrator([gateway()])
    response = orch.parse_payment_response(gateway(), request(), {"ResponseCode": 0, "LowProfileId": "lp1", "Url": "https://pay.test/lp1"})
    assert response.status == pgi.PaymentStatus.REQUIRES_ACTION
    assert response.redirect_url.endswith("lp1")


def test_parse_declined_response():
    orch = pgi.IsraeliPaymentOrchestrator([gateway()])
    response = orch.parse_payment_response(gateway(), request(), {"status": "declined", "code": "issuer_declined"})
    assert response.status == pgi.PaymentStatus.DECLINED


def test_charge_success_uses_transport():
    transport = FakeTransport(responses=[{"success": True, "transaction_id": "tx1", "status": "approved"}])
    orch = pgi.IsraeliPaymentOrchestrator([gateway("grow")], transport=transport)
    response = orch.charge(request())
    assert response.approved
    assert response.gateway == "grow"
    assert transport.calls[0]["method"] == "POST"


def test_idempotency_returns_cached_response():
    transport = FakeTransport(responses=[{"success": True, "transaction_id": "tx1", "status": "approved"}, {"success": True, "transaction_id": "tx2", "status": "approved"}])
    orch = pgi.IsraeliPaymentOrchestrator([gateway("grow")], transport=transport)
    first = orch.charge(request())
    second = orch.charge(request())
    assert first.transaction_id == second.transaction_id == "tx1"
    assert len(transport.calls) == 1


def test_fallback_on_timeout_without_transaction_id():
    timeout = pgi.PaymentGatewayError("timeout", code="network_timeout", retryable=True)
    transport = FakeTransport(responses=[{"success": True, "transaction_id": "tx2", "status": "approved"}], failures=[timeout])
    orch = pgi.IsraeliPaymentOrchestrator([gateway("cardcom", priority=1), gateway("grow", priority=2)], transport=transport)
    response = orch.charge(request())
    assert response.gateway == "grow"
    assert response.transaction_id == "tx2"
    assert len(transport.calls) == 2


def test_no_fallback_when_transaction_id_exists_in_error():
    error = pgi.PaymentGatewayError("unknown", code="network_timeout", retryable=True, transaction_id="tx-known")
    transport = FakeTransport(failures=[error])
    orch = pgi.IsraeliPaymentOrchestrator([gateway("cardcom"), gateway("grow", priority=20)], transport=transport)
    with pytest.raises(pgi.PaymentGatewayError):
        orch.charge(request())


def test_no_fallback_on_issuer_decline_response():
    transport = FakeTransport(responses=[{"status": "declined", "code": "issuer_declined"}])
    orch = pgi.IsraeliPaymentOrchestrator([gateway("cardcom"), gateway("grow", priority=20)], transport=transport)
    response = orch.charge(request())
    assert response.status == pgi.PaymentStatus.DECLINED
    assert len(transport.calls) == 1


def test_refund_success_maps_to_refunded():
    transport = FakeTransport(responses=[{"success": True, "refund_id": "rf1", "status": "approved"}])
    orch = pgi.IsraeliPaymentOrchestrator([gateway("grow")], transport=transport)
    response = orch.refund("grow", pgi.RefundRequest(transaction_id="tx1", amount_agorot=1000, reason="partial"))
    assert response.status == pgi.PaymentStatus.REFUNDED
    assert response.refund_id == "rf1"


def test_refund_requires_capability():
    cfg = gateway("grow", capabilities={"hosted_checkout"})
    orch = pgi.IsraeliPaymentOrchestrator([cfg], transport=FakeTransport())
    with pytest.raises(pgi.PaymentGatewayError) as err:
        orch.refund("grow", pgi.RefundRequest(transaction_id="tx1", amount_agorot=1000))
    assert err.value.code == "refund_unsupported"


def test_status_uses_get():
    transport = FakeTransport(responses=[{"success": True, "transaction_id": "tx1", "amount_agorot": 1000, "status": "approved"}])
    orch = pgi.IsraeliPaymentOrchestrator([gateway("grow")], transport=transport)
    response = orch.status("grow", "tx1")
    assert response.approved
    assert transport.calls[0]["method"] == "GET"


def test_webhook_signature_validates():
    orch = pgi.IsraeliPaymentOrchestrator([gateway("cardcom")])
    payload = b'{"order_id":"INV-1"}'
    signature = orch.sign_webhook_payload("cardcom", payload)
    assert orch.verify_webhook("cardcom", payload, signature)


def test_webhook_signature_rejects_wrong_payload():
    orch = pgi.IsraeliPaymentOrchestrator([gateway("cardcom")])
    signature = orch.sign_webhook_payload("cardcom", b"original")
    assert not orch.verify_webhook("cardcom", b"changed", signature)


def test_request_from_dict_accepts_decimal_amount():
    req = pgi.request_from_dict({"order_id": "INV-2", "amount": "12.34"})
    assert req.amount_agorot == 1234


def test_response_to_dict_serializes_enum():
    response = pgi.PaymentResponse(gateway="grow", status=pgi.PaymentStatus.APPROVED)
    assert pgi.response_to_dict(response)["status"] == "approved"


def test_redact_mapping_redacts_nested_secrets():
    redacted = pgi.redact_mapping({"api_key": "abc", "nested": {"token": "tok", "safe": "ok"}})
    assert redacted["api_key"] == "***REDACTED***"
    assert redacted["nested"]["token"] == "***REDACTED***"
    assert redacted["nested"]["safe"] == "ok"


@pytest.mark.asyncio
async def test_async_charge_success():
    transport = AsyncFakeTransport(responses=[{"success": True, "transaction_id": "async1", "status": "approved"}])
    orch = pgi.AsyncIsraeliPaymentOrchestrator([gateway("grow")], transport=transport)
    response = await orch.charge(request())
    assert response.approved
    assert response.transaction_id == "async1"


@pytest.mark.asyncio
async def test_async_refund_success():
    transport = AsyncFakeTransport(responses=[{"success": True, "refund_id": "arf1", "status": "approved"}])
    orch = pgi.AsyncIsraeliPaymentOrchestrator([gateway("grow")], transport=transport)
    response = await orch.refund("grow", pgi.RefundRequest(transaction_id="tx1", amount_agorot=1000))
    assert response.status == pgi.PaymentStatus.REFUNDED


def test_capture_requires_capability():
    cfg = gateway("grow", capabilities={"hosted_checkout"})
    orch = pgi.IsraeliPaymentOrchestrator([cfg], transport=FakeTransport())
    with pytest.raises(pgi.PaymentGatewayError) as err:
        orch.capture("grow", "tx1", 1000)
    assert err.value.code == "capture_unsupported"


def test_capture_success():
    transport = FakeTransport(responses=[{"success": True, "transaction_id": "cap1", "status": "approved"}])
    orch = pgi.IsraeliPaymentOrchestrator([gateway("grow")], transport=transport)
    response = orch.capture("grow", "auth1", 1000)
    assert response.approved
    assert transport.calls[0]["json_body"]["amount"] == "10.00"
