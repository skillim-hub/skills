from __future__ import annotations

import csv
import json
import sys
from decimal import Decimal
from pathlib import Path

import pytest
from typer.testing import CliRunner

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from prepayment_deposit_handler_client import (
    AsyncPrepaymentDepositClient,
    BusinessType,
    DepositError,
    DepositNature,
    DocumentType,
    LineItem,
    Money,
    PrepaymentDepositClient,
    build_deposit_record,
    classify_deposit,
    main,
    parse_date,
    settle_invoice,
    vat_rate_for_date,
)
from prepayment_deposit_handler_cli import app

runner = CliRunner()


def test_money_rounds_half_up():
    assert Money("10.005").amount == Decimal("10.01")


def test_money_rejects_negative():
    with pytest.raises(DepositError):
        Money("-0.01")


def test_line_item_calculates_vat_and_gross():
    item = LineItem("consulting", 2, "100", "0.18")
    assert item.net == Decimal("200.00")
    assert item.vat == Decimal("36.00")
    assert item.gross == Decimal("236.00")


def test_line_item_rejects_zero_quantity():
    with pytest.raises(DepositError):
        LineItem("bad", 0, 100)


def test_parse_date_iso():
    assert parse_date("2026-01-31").isoformat() == "2026-01-31"


def test_parse_date_israeli_format():
    assert parse_date("31-01-2026").isoformat() == "2026-01-31"


def test_vat_rate_default():
    assert vat_rate_for_date("2026-01-01") == Decimal("0.18")


def test_settle_basic_vat_registered():
    result = settle_invoice([LineItem("project", 1, "1000", "0.18")], "300")
    assert result.total_inc_vat.amount == Decimal("1180.00")
    assert result.deposit_applied.amount == Decimal("300.00")
    assert result.balance_due.amount == Decimal("880.00")
    assert DocumentType.FINAL_TAX_INVOICE in result.recommended_documents


def test_settle_vat_exempt_has_no_vat():
    result = settle_invoice([LineItem("lesson", 1, "1000", "0.18")], "100", business_type=BusinessType.VAT_EXEMPT)
    assert result.vat.amount == Decimal("0.00")
    assert result.total_inc_vat.amount == Decimal("1000.00")
    assert result.recommended_documents == [DocumentType.RECEIPT]


def test_settle_overpayment_warns_refund():
    result = settle_invoice([LineItem("small job", 1, "100", "0.18")], "200")
    assert result.overpayment.amount == Decimal("82.00")
    assert DocumentType.REFUND_RECEIPT in result.recommended_documents
    assert any("exceeds" in w for w in result.warnings)


def test_settle_no_line_items_error():
    with pytest.raises(DepositError):
        settle_invoice([], "0")


def test_classify_security_deposit_receipt_only_on_receive():
    rec = classify_deposit(DepositNature.SECURITY_DEPOSIT_HELD_IN_TRUST, BusinessType.VAT_REGISTERED, refundable=True)
    assert rec.receive_documents == [DocumentType.RECEIPT]
    assert DocumentType.FINAL_TAX_INVOICE in rec.settlement_documents


def test_classify_vat_exempt_does_not_recommend_tax_invoice():
    rec = classify_deposit(DepositNature.ADVANCE_FOR_TAXABLE_SUPPLY, BusinessType.VAT_EXEMPT, refundable=False)
    assert DocumentType.TAX_INVOICE not in rec.receive_documents
    assert rec.receive_documents == [DocumentType.RECEIPT]


def test_classify_non_refundable_fee_recommends_tax_invoice_receipt():
    rec = classify_deposit(DepositNature.NON_REFUNDABLE_BOOKING_FEE, BusinessType.VAT_REGISTERED, refundable=False)
    assert DocumentType.TAX_INVOICE_RECEIPT in rec.receive_documents


def test_build_deposit_record_remaining():
    rec = build_deposit_record(
        deposit_id="D-1",
        contract_id="C-1",
        received_date="01-02-2026",
        amount="500",
        payer_name="Customer",
        payee_name="Supplier",
        nature=DepositNature.REFUNDABLE_BOOKING_DEPOSIT,
        refundable=True,
        applied_amount="125",
    )
    assert rec.remaining.amount == Decimal("375.00")


def test_build_deposit_record_rejects_overapplied():
    with pytest.raises(DepositError):
        build_deposit_record(
            deposit_id="D-1",
            contract_id="C-1",
            received_date="2026-02-01",
            amount="100",
            payer_name="Customer",
            payee_name="Supplier",
            nature=DepositNature.REFUNDABLE_BOOKING_DEPOSIT,
            applied_amount="101",
        )


def test_client_export_csv(tmp_path):
    client = PrepaymentDepositClient()
    rec = client.create_record(
        deposit_id="D-2",
        contract_id="C-2",
        received_date="2026-02-01",
        amount="400",
        payer_name="A",
        payee_name="B",
        nature=DepositNature.ADVANCE_FOR_TAXABLE_SUPPLY,
    )
    path = client.export_records_csv([rec], tmp_path / "records.csv")
    assert path.exists()
    rows = list(csv.DictReader(path.open(encoding="utf-8-sig")))
    assert rows[0]["deposit_id"] == "D-2"
    assert rows[0]["remaining"] == "400.00"


@pytest.mark.asyncio
async def test_async_client_settle():
    client = AsyncPrepaymentDepositClient()
    result = await client.settle([LineItem("async", 1, "100")], "10")
    assert result.balance_due.amount == Decimal("108.00")


@pytest.mark.asyncio
async def test_async_client_classify():
    client = AsyncPrepaymentDepositClient()
    result = await client.classify(DepositNature.GIFT_CARD_OR_CREDIT_BALANCE, BusinessType.VAT_REGISTERED, refundable=True)
    assert DocumentType.RECEIPT in result.receive_documents


def test_argparse_main_settle_outputs_json(capsys):
    rc = main(["settle", "--line", "job:1:100:0.18", "--deposit", "18"])
    captured = capsys.readouterr().out
    data = json.loads(captured)
    assert rc == 0
    assert data["balance_due"]["amount"] == "100.00"


def test_typer_classify_command():
    result = runner.invoke(app, ["classify", "--nature", "security_deposit_held_in_trust", "--business-type", "osek_murshe", "--refundable"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert "receipt" in data["receive_documents"]


def test_typer_settle_command():
    result = runner.invoke(app, ["settle", "--line", "job:1:100:0.18", "--deposit", "18"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["total_inc_vat"]["amount"] == "118.00"


def test_typer_record_command_exports_csv(tmp_path):
    out = tmp_path / "one.csv"
    result = runner.invoke(app, [
        "record",
        "--deposit-id", "D3",
        "--contract-id", "C3",
        "--received-date", "03-03-2026",
        "--amount", "250",
        "--payer-name", "לקוח",
        "--payee-name", "עסק",
        "--nature", "refundable_booking_deposit",
        "--output-csv", str(out),
    ])
    assert result.exit_code == 0
    assert out.exists()


def test_multi_line_settlement_sums_correctly():
    result = settle_invoice([LineItem("a", 1, "100"), LineItem("b", 3, "50")], "100")
    assert result.subtotal_ex_vat.amount == Decimal("250.00")
    assert result.vat.amount == Decimal("45.00")
    assert result.balance_due.amount == Decimal("195.00")


def test_currency_mismatch_add_raises():
    with pytest.raises(DepositError):
        _ = Money("1", "ILS") + Money("1", "USD")


def test_cli_async_demo():
    result = runner.invoke(app, ["async-demo"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["total_inc_vat"]["amount"] == "1180.00"


def test_invalid_vat_rate():
    with pytest.raises(DepositError):
        LineItem("bad", 1, "100", "18")


def test_record_cli_json():
    result = runner.invoke(app, [
        "record", "--deposit-id", "D4", "--contract-id", "C4",
        "--received-date", "2026-03-03", "--amount", "100",
        "--payer-name", "Customer", "--payee-name", "Supplier",
        "--nature", "advance_for_taxable_supply"
    ])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["remaining"]["amount"] == "100.00"


def test_parse_date_slash_israeli_format():
    assert parse_date("31/01/2026").isoformat() == "2026-01-31"


def test_settle_keeps_deposit_reference():
    result = settle_invoice([LineItem("project", 1, "1000", "0.18")], "300", deposit_reference="DEP-1")
    assert result.deposit_reference == "DEP-1"
    assert result.as_dict()["deposit_reference"] == "DEP-1"
