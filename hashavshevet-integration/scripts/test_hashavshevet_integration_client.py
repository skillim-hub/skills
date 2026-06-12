from __future__ import annotations

import asyncio
import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from hashavshevet_integration_client import (  # noqa: E402
    AsyncHashavshevetIntegrationClient,
    BTKNEntry,
    CompanyContext,
    CustomerSupplier,
    HashavshevetIntegrationClient,
    JournalEntry,
    JournalEntryLine,
    ValidationError,
    build_openformat_skeleton,
    calculate_vat,
    format_money,
    generate_btkn_file,
    gross_from_net,
    invoice_allocation_threshold,
    is_plausible_israeli_vat_number,
    normalize_vat_number,
    parse_fixed_width_lines,
    read_csv_auto,
    requires_allocation_number,
    validate_invoice_payload,
    write_csv_utf8_bom,
)


def test_normalize_and_validate_vat_number() -> None:
    assert normalize_vat_number("514-087-337") == "514087337"
    assert is_plausible_israeli_vat_number("514087337") is True
    assert is_plausible_israeli_vat_number("111111111") is False


def test_vat_calculation_uses_2026_rate() -> None:
    assert calculate_vat("100.00") == Decimal("18.00")
    assert gross_from_net("100.00") == Decimal("118.00")
    assert format_money(Decimal("10.235")) == "10.24"


def test_allocation_thresholds_by_date() -> None:
    assert invoice_allocation_threshold("2025-05-01") == Decimal("20000")
    assert invoice_allocation_threshold("2026-01-01") == Decimal("10000")
    assert invoice_allocation_threshold("01-06-2026") == Decimal("5000")


def test_requires_allocation_number_only_when_all_conditions_hold() -> None:
    assert requires_allocation_number("10000.01", "2026-01-02", customer_vat_number="514087337") is True
    assert requires_allocation_number("10000.00", "2026-01-02", customer_vat_number="514087337") is False
    assert requires_allocation_number("20000", "2026-01-02", document_type="receipt", customer_vat_number="514087337") is False
    assert requires_allocation_number("20000", "2026-01-02", customer_vat_number=None) is False


def test_journal_entry_balance_validation() -> None:
    entry = JournalEntry(
        entry_id="JE-1",
        entry_date=date(2026, 6, 5),
        company_id="514087337",
        lines=(
            JournalEntryLine("1100", debit=Decimal("118.00")),
            JournalEntryLine("4000", credit=Decimal("100.00")),
            JournalEntryLine("2650", credit=Decimal("18.00")),
        ),
    )
    entry.validate()
    assert entry.is_balanced()


def test_unbalanced_journal_entry_raises() -> None:
    entry = JournalEntry(
        entry_id="JE-2",
        entry_date=date(2026, 6, 5),
        company_id="514087337",
        lines=(JournalEntryLine("1100", debit=Decimal("10.00")),),
    )
    with pytest.raises(ValidationError):
        entry.validate()


def test_fixed_width_parser_extracts_fields() -> None:
    lines = ["0001  לקוח א         118.00"]
    schema = {"id": (0, 4), "name": (6, 20), "amount": (20, 30)}
    parsed = parse_fixed_width_lines(lines, schema)
    assert parsed[0]["id"] == "0001"
    assert parsed[0]["name"] == "לקוח א"
    assert parsed[0]["amount"] == "118.00"


def test_csv_round_trip_handles_hebrew(tmp_path: Path) -> None:
    target = tmp_path / "customers.csv"
    write_csv_utf8_bom([{"account": "100", "name": "לקוח בדיקה"}], target)
    rows = read_csv_auto(target)
    assert rows == [{"account": "100", "name": "לקוח בדיקה"}]


def test_generate_btkn_file_writes_windows_1255(tmp_path: Path) -> None:
    target = tmp_path / "BTKN.TXT"
    generate_btkn_file([
        BTKNEntry(
            company_id="514087337",
            entry_id="1",
            entry_date=date(2026, 6, 5),
            debit_account="1100",
            credit_account="4000",
            net_amount=Decimal("100"),
            vat_amount=Decimal("18"),
            description="מכירה",
        )
    ], target)
    text = target.read_text(encoding="windows-1255")
    assert "BTKN1|514087337|1|05-06-2026|1100|4000|100.00|18.00" in text


def test_validate_invoice_payload_reports_missing_fields() -> None:
    errors = validate_invoice_payload({"company_id": "514087337"})
    assert "Missing required field: invoice_number" in errors
    assert "Missing required field: net_amount" in errors


def test_sync_client_posts_customer_supplier() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/accounts"
        assert request.headers["Authorization"] == "Bearer token"
        body = json.loads(request.content.decode())
        assert body["vat_number"] == "514087337"
        return httpx.Response(200, json={"ok": True, "id": body["account_id"]})

    client = HashavshevetIntegrationClient(
        "https://example.test",
        token="token",
        transport=httpx.MockTransport(handler),
    )
    result = client.sync_customer_supplier(CustomerSupplier("C100", "לקוח", vat_number="514087337"))
    assert result == {"ok": True, "id": "C100"}


def test_async_client_gets_json() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/journal-transactions"
        return httpx.Response(200, json={"records": [{"entry_id": "1"}]})

    async def run() -> dict:
        client = AsyncHashavshevetIntegrationClient(
            "https://example.test",
            token="token",
            transport=httpx.MockTransport(handler),
        )
        return await client.aget_json("/journal-transactions")

    result = asyncio.run(run())
    assert result["records"][0]["entry_id"] == "1"


def test_openformat_skeleton_contains_ini_and_data() -> None:
    company = CompanyContext("514087337", "בדיקה בעמ")
    entry = JournalEntry(
        entry_id="JE-3",
        entry_date=date(2026, 6, 5),
        company_id="514087337",
        lines=(
            JournalEntryLine("1100", debit=Decimal("118.00")),
            JournalEntryLine("4000", credit=Decimal("118.00")),
        ),
        memo="בדיקה",
    )
    files = build_openformat_skeleton(company, [entry])
    assert "B100Count=1" in files["INI.TXT"]
    assert files["BKMVDATA.TXT"].startswith("A100|514087337")
