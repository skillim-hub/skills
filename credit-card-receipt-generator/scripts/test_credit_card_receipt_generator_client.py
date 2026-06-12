from __future__ import annotations

import asyncio
import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).resolve().parent))

from credit_card_receipt_generator_cli import main
from credit_card_receipt_generator_client import (
    CreditCardReceiptClient,
    Gateway,
    ReceiptRecord,
    ReceiptValidationError,
    allocation_threshold_for,
    contains_raw_pan,
    is_valid_israeli_id,
    normalize_gateway_payload,
    provider_endpoint,
    split_gross_amount,
)


def test_split_gross_standard_vat():
    vat = split_gross_amount(Decimal("118.00"))
    assert vat.net == Decimal("100.00")
    assert vat.vat == Decimal("18.00")
    assert vat.gross == Decimal("118.00")


def test_split_gross_exempt_dealer():
    vat = split_gross_amount(Decimal("400.00"), exempt_dealer=True)
    assert vat.net == Decimal("400.00")
    assert vat.vat == Decimal("0.00")
    assert vat.exempt_dealer is True


def test_israeli_id_checksum_valid_and_invalid():
    assert is_valid_israeli_id("515123453") is True
    assert is_valid_israeli_id("123456789") is False


def test_raw_pan_detection_rejects_luhn_card():
    assert contains_raw_pan({"card": "4580000000000000"}) is True
    assert contains_raw_pan({"masked": "45******0000"}) is False


def test_normalize_cardcom_success():
    result = normalize_gateway_payload(
        Gateway.CARDCOM,
        {"ResponseCode": 0, "TranzactionId": "123", "ApprovalNumber": "ABC", "Amount": "118.00", "Last4": "1234"},
    )
    assert result.success is True
    assert result.transaction_id == "123"
    assert result.approval_number == "ABC"
    assert result.masked_card == "****1234"


def test_normalize_grow_success():
    result = normalize_gateway_payload(
        "grow",
        {"status": "success", "transactionId": "G1", "asmachta": "A1", "sum": "50.00", "cardSuffix": "9876"},
    )
    assert result.gateway == Gateway.GROW
    assert result.success is True
    assert result.amount == Decimal("50.00")


def test_normalize_pelecard_success():
    result = normalize_gateway_payload(
        "pelecard",
        {"StatusCode": "000", "ShvaResult": "000", "PelecardTransactionId": "P1", "VoucherId": "86-001-006", "total": "118.00"},
    )
    assert result.success is True
    assert result.approval_number == "86-001-006"


def test_receipt_markdown_contains_vat_and_transaction():
    client = CreditCardReceiptClient()
    record = ReceiptRecord(
        gateway=Gateway.CARDCOM,
        business_name="Kinneret Studio",
        business_tax_id="515123453",
        customer_name="Dana Levi",
        amount=Decimal("118.00"),
        currency="ILS",
        payment_date=date(2026, 6, 4),
        transaction_id="T123",
        approval_number="A123",
        receipt_number="R1",
        masked_card="****1234",
    )
    text = client.create_receipt(record)
    assert "Transaction ID: T123" in text
    assert "VAT amount: ₪18.00" in text
    assert "04-06-2026" in text


def test_receipt_json_parses():
    client = CreditCardReceiptClient()
    payload = {"ResponseCode": 0, "TranzactionId": "123", "ApprovalNumber": "ABC", "Amount": "118.00"}
    text = client.create_receipt_from_gateway(
        "cardcom",
        payload,
        business_name="Kinneret Studio",
        business_tax_id="515123453",
        customer_name="Dana Levi",
        receipt_number="R2",
        payment_date=date(2026, 1, 5),
        output_format="json",
    )
    data = json.loads(text)
    assert data["payment"]["gateway"] == "cardcom"
    assert data["vat"]["gross"] == "₪118.00"


def test_failed_gateway_is_blocked():
    client = CreditCardReceiptClient()
    with pytest.raises(ReceiptValidationError):
        client.create_receipt_from_gateway(
            "cardcom",
            {"ResponseCode": 99, "Description": "declined", "Amount": "10.00"},
            business_name="Biz",
            business_tax_id="515123453",
        )


def test_allocation_threshold_dates():
    assert allocation_threshold_for(date(2026, 1, 1)) == Decimal("10000")
    assert allocation_threshold_for(date(2026, 6, 1)) == Decimal("5000")


def test_provider_endpoint_lookup():
    spec = provider_endpoint("tranzila", "payment_request")
    assert spec["method"] == "POST"
    assert spec["url"].endswith("/v1/pr/create")


def test_async_receipt_generation():
    client = CreditCardReceiptClient()
    record = ReceiptRecord(
        gateway=Gateway.GROW,
        business_name="Sample Business",
        business_tax_id="515123453",
        customer_name="Sample Customer",
        amount=Decimal("50.00"),
        currency="ILS",
        payment_date=date(2026, 6, 4),
        transaction_id="G1",
        approval_number="A1",
        receipt_number="R3",
        exempt_dealer=True,
    )
    text = asyncio.run(client.async_create_receipt(record))
    assert "Osek Patur" in text
    assert "₪0.00" in text


def test_cli_from_json(tmp_path):
    payload_path = tmp_path / "payload.json"
    payload_path.write_text(json.dumps({"ResponseCode": 0, "TranzactionId": "123", "ApprovalNumber": "ABC", "Amount": "118.00"}), encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "from-json",
            str(payload_path),
            "--gateway",
            "cardcom",
            "--business-name",
            "Kinneret Studio",
            "--business-tax-id",
            "515123453",
            "--customer-name",
            "Dana Levi",
            "--receipt-number",
            "R4",
            "--date",
            "04-06-2026",
        ],
    )
    assert result.exit_code == 0, result.output
    assert "Receipt R4" in result.output
    assert "₪18.00" in result.output


def test_cli_endpoint():
    runner = CliRunner()
    result = runner.invoke(main, ["endpoint", "pelecard", "add_receipt"])
    assert result.exit_code == 0
    assert "gateway21.pelecard.biz" in result.output
