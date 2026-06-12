from __future__ import annotations

import asyncio
import csv
import json
import subprocess
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

import invoice_aging_collection_client as m


ROOT = Path(__file__).resolve().parents[1]
CLI_PATH = ROOT / "scripts" / "invoice-aging-collection-cli.py"


def ledger_with_invoice(**invoice_overrides):
    invoice = {
        "invoice_id": "INV-X",
        "client_id": "c-1",
        "issue_date": "01/01/2026",
        "due_date": "31/01/2026",
        "amount": "2500.00",
        "currency": "ILS",
        "status": "open",
        "partial_payments": [],
    }
    invoice.update(invoice_overrides)
    return {
        "business": {
            "name": "סטודיו בדיקה",
            "payment_instructions": "בנק 12 סניף 345 חשבון 67890",
        },
        "clients": [
            {
                "client_id": "c-1",
                "name": "לקוח בדיקה בע\"מ",
                "email": "client@example.co.il",
                "whatsapp": "050-123-4567",
                "mailing_address": "רחוב הבדיקה 1, תל אביב",
            }
        ],
        "invoices": [invoice],
        "blocked_dates": ["23/04/2026"],
    }


def test_parse_dd_mm_yyyy_with_slashes():
    assert m.parse_date("15/04/2026") == date(2026, 4, 15)


def test_parse_iso_date():
    assert m.parse_date("2026-04-15") == date(2026, 4, 15)


def test_format_date_is_israeli():
    assert m.format_date(date(2026, 4, 15)) == "15/04/2026"


def test_format_money_ils_symbol():
    assert m.format_money(Decimal("1234.5")) == "₪1,234.50"


def test_money_rounding():
    assert m.money("10.235") == Decimal("10.24")


def test_end_of_month_february_leap_year():
    assert m.end_of_month(date(2024, 2, 5)) == date(2024, 2, 29)


def test_default_due_date_end_of_month_plus_45():
    invoice = m.invoice_from_dict({
        "invoice_id": "INV-D",
        "client_id": "c-1",
        "issue_date": "10/01/2026",
        "amount": "100.00",
        "currency": "ILS",
        "status": "open",
    })
    assert invoice.resolved_due_date() == date(2026, 3, 17)


def test_payment_terms_due_date():
    invoice = m.invoice_from_dict({
        "invoice_id": "INV-T",
        "client_id": "c-1",
        "issue_date": "01/01/2026",
        "payment_terms_days": 30,
        "amount": "100.00",
        "currency": "ILS",
        "status": "open",
    })
    assert invoice.resolved_due_date() == date(2026, 1, 31)


@pytest.mark.parametrize(
    ("as_of", "bucket", "stage"),
    [
        ("30/01/2026", "not_due", "none"),
        ("10/02/2026", "current", "none"),
        ("07/03/2026", "30", "friendly_whatsapp"),
        ("22/03/2026", "45", "followup_whatsapp"),
        ("06/04/2026", "60", "formal_email"),
        ("21/04/2026", "75", "legal_warning"),
        ("10/05/2026", "90_plus", "final_notice"),
    ],
)
def test_bucket_and_stage_boundaries(as_of, bucket, stage):
    client = m.InvoiceAgingClient(ledger_with_invoice())
    record = client.aging_records(as_of)[0]
    assert record.bucket.value == bucket
    assert record.stage.value == stage


def test_paid_invoice_excluded_from_reminders():
    client = m.InvoiceAgingClient(ledger_with_invoice(status="paid", paid_date="01/02/2026"))
    assert client.reminders_due("10/05/2026") == []
    assert client.aging_records("10/05/2026")[0].bucket.value == "paid"


def test_cancelled_invoice_excluded_from_reminders():
    client = m.InvoiceAgingClient(ledger_with_invoice(status="cancelled"))
    assert client.reminders_due("10/05/2026") == []
    assert client.aging_records("10/05/2026")[0].bucket.value == "cancelled"


def test_disputed_invoice_excluded_from_reminders():
    client = m.InvoiceAgingClient(ledger_with_invoice(status="disputed", dispute_reason="amount_mismatch"))
    assert client.reminders_due("10/05/2026") == []
    assert client.aging_records("10/05/2026")[0].bucket.value == "disputed"


def test_partial_payment_reduces_outstanding():
    client = m.InvoiceAgingClient(ledger_with_invoice(partial_payments=[{"date": "10/03/2026", "amount": "500.00"}]))
    record = client.aging_records("15/04/2026")[0]
    assert record.outstanding_amount == Decimal("2000.00")
    reminder = client.render_for_invoice("INV-X", "formal_email", "15/04/2026")
    assert "₪2,000.00" in reminder.body


def test_overpayment_validation_error():
    client = m.InvoiceAgingClient(ledger_with_invoice(partial_payments=[{"date": "10/03/2026", "amount": "3000.00"}]))
    codes = {issue.code for issue in client.validate()}
    assert "PARTIAL_PAYMENTS_EXCEED_AMOUNT" in codes


def test_unknown_client_validation_error():
    ledger = ledger_with_invoice(client_id="missing")
    client = m.InvoiceAgingClient(ledger)
    codes = {issue.code for issue in client.validate()}
    assert "UNKNOWN_CLIENT" in codes


def test_duplicate_invoice_validation_error():
    ledger = ledger_with_invoice()
    ledger["invoices"].append(dict(ledger["invoices"][0]))
    client = m.InvoiceAgingClient(ledger)
    codes = {issue.code for issue in client.validate()}
    assert "DUPLICATE_INVOICE_ID" in codes


def test_unsupported_currency_validation_error():
    client = m.InvoiceAgingClient(ledger_with_invoice(currency="USD"))
    codes = {issue.code for issue in client.validate()}
    assert "UNSUPPORTED_CURRENCY" in codes


def test_due_before_issue_warning():
    client = m.InvoiceAgingClient(ledger_with_invoice(issue_date="10/01/2026", due_date="01/01/2026"))
    issues = client.validate()
    assert any(issue.code == "DUE_BEFORE_ISSUE" and issue.severity.value == "warning" for issue in issues)


def test_paid_date_open_status_warning():
    client = m.InvoiceAgingClient(ledger_with_invoice(paid_date="01/02/2026"))
    issues = client.validate()
    assert any(issue.code == "PAID_DATE_OPEN_STATUS" and issue.severity.value == "warning" for issue in issues)


def test_phone_normalization_local_mobile():
    assert m.normalize_israeli_phone("050-123-4567") == "+972501234567"


def test_invalid_phone_raises():
    with pytest.raises(ValueError):
        m.normalize_israeli_phone("12345")


def test_next_business_day_skips_friday_and_saturday():
    assert m.next_business_day(date(2026, 4, 24)) == date(2026, 4, 26)
    assert m.next_business_day(date(2026, 4, 25)) == date(2026, 4, 26)


def test_next_business_day_skips_blocked_date():
    assert m.next_business_day(date(2026, 4, 23), {date(2026, 4, 23)}) == date(2026, 4, 26)


def test_reminders_channel_filter_whatsapp():
    client = m.InvoiceAgingClient(ledger_with_invoice())
    reminders = client.reminders_due("07/03/2026", channel="whatsapp")
    assert len(reminders) == 1
    assert reminders[0].channel.value == "whatsapp"


def test_missing_whatsapp_blocks_whatsapp_reminder():
    ledger = ledger_with_invoice()
    ledger["clients"][0]["whatsapp"] = ""
    client = m.InvoiceAgingClient(ledger)
    assert client.reminders_due("07/03/2026", channel="whatsapp") == []


def test_missing_email_blocks_email_reminder():
    ledger = ledger_with_invoice()
    ledger["clients"][0]["email"] = ""
    client = m.InvoiceAgingClient(ledger)
    assert client.reminders_due("06/04/2026", channel="email") == []


def test_legal_warning_requires_human_review():
    client = m.InvoiceAgingClient(ledger_with_invoice())
    reminder = client.render_for_invoice("INV-X", "legal_warning", "21/04/2026")
    assert reminder.requires_human_review is True
    assert "14 ימים" in reminder.body


def test_send_due_blocks_live_formal_without_approval():
    client = m.InvoiceAgingClient(ledger_with_invoice())
    results = client.send_due("06/04/2026", dry_run=False, require_approval=True)
    assert results[0]["delivery_status"] == "blocked_human_review_required"


def test_send_due_dry_run_returns_hash():
    client = m.InvoiceAgingClient(ledger_with_invoice())
    results = client.send_due("07/03/2026", dry_run=True)
    assert results[0]["delivery_status"] == "dry_run"
    assert results[0]["message_hash"].startswith("sha256:")


@pytest.mark.asyncio
async def test_async_send_due_dry_run():
    client = m.InvoiceAgingClient(ledger_with_invoice())
    results = await client.async_send_due("07/03/2026", dry_run=True)
    assert results[0]["delivery_status"] == "dry_run"


def test_payment_promise_pauses_reminders():
    client = m.InvoiceAgingClient(ledger_with_invoice(promised_payment_date="10/05/2026"))
    assert client.reminders_due("06/04/2026") == []


def test_client_summary_aggregates_multiple_invoices():
    ledger = ledger_with_invoice()
    ledger["invoices"].append({
        "invoice_id": "INV-Y",
        "client_id": "c-1",
        "issue_date": "01/02/2026",
        "due_date": "28/02/2026",
        "amount": "1000.00",
        "currency": "ILS",
        "status": "open",
        "partial_payments": [],
    })
    client = m.InvoiceAgingClient(ledger)
    summary = client.client_summary("15/04/2026")
    assert summary[0]["invoice_count"] == 2
    assert summary[0]["outstanding_amount"] == "3500.00"


def test_evidence_pack_contains_checklist():
    client = m.InvoiceAgingClient(ledger_with_invoice())
    pack = client.evidence_pack("c-1", "15/04/2026")
    assert pack["client"]["client_id"] == "c-1"
    assert "invoice copy" in pack["evidence_checklist"]


def test_import_csv(tmp_path):
    csv_path = tmp_path / "invoices.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "invoice_id",
                "client_id",
                "client_name",
                "issue_date",
                "due_date",
                "amount",
                "currency",
                "status",
                "email",
                "whatsapp",
                "mailing_address",
            ],
        )
        writer.writeheader()
        writer.writerow({
            "invoice_id": "INV-CSV",
            "client_id": "c-csv",
            "client_name": "לקוח CSV",
            "issue_date": "01/01/2026",
            "due_date": "31/01/2026",
            "amount": "100.00",
            "currency": "ILS",
            "status": "open",
            "email": "csv@example.co.il",
            "whatsapp": "0501234567",
            "mailing_address": "כתובת",
        })
    ledger = m.import_csv(csv_path)
    assert ledger["clients"][0]["client_id"] == "c-csv"
    assert ledger["invoices"][0]["invoice_id"] == "INV-CSV"


def test_save_and_load_ledger(tmp_path):
    path = tmp_path / "ledger.json"
    m.save_ledger(path, m.sample_ledger())
    loaded = m.load_ledger(path)
    assert loaded["business"]["name"] == "סטודיו דוגמה"


def test_cli_sample_and_age(tmp_path):
    ledger_path = tmp_path / "sample.json"
    subprocess.run([sys.executable, str(CLI_PATH), "sample-data", "--out", str(ledger_path)], check=True)
    result = subprocess.run(
        [sys.executable, str(CLI_PATH), "age", str(ledger_path), "--as-of", "15/04/2026"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["as_of"] == "15/04/2026"
    assert payload["totals"]["open_invoices"] >= 1


def test_cli_render(tmp_path):
    ledger_path = tmp_path / "sample.json"
    m.save_ledger(ledger_path, m.sample_ledger())
    result = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "render",
            str(ledger_path),
            "--invoice-id",
            "INV-100",
            "--stage",
            "formal_email",
            "--as-of",
            "15/04/2026",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "דרישת תשלום" in result.stdout
    assert "INV-100" in result.stdout


def test_parse_legacy_dd_mm_yyyy_with_hyphens():
    assert m.parse_date("15/04/2026") == date(2026, 4, 15)


def test_create_invoice_record_generates_next_id():
    record = m.create_invoice_record(
        client_id="c-1",
        issue_date="01/04/2026",
        due_date="30/04/2026",
        amount="1800.00",
        existing_invoice_ids=["INV-100", "INV-101"],
    )
    assert record["invoice_id"] == "INV-102"
    assert record["issue_date"] == "01/04/2026"


def test_cli_create_invoice_chain(tmp_path):
    ledger_path = tmp_path / "sample.json"
    m.save_ledger(ledger_path, m.sample_ledger())
    result = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "create-invoice",
            str(ledger_path),
            "--client-id",
            "c-100",
            "--issue-date",
            "01/04/2026",
            "--due-date",
            "30/04/2026",
            "--amount",
            "1800.00",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    invoice_id = payload["invoice_id"]
    render_result = subprocess.run(
        [
            sys.executable,
            str(CLI_PATH),
            "render",
            str(ledger_path),
            "--invoice-id",
            invoice_id,
            "--stage",
            "friendly_whatsapp",
            "--as-of",
            "01/06/2026",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    reminder = json.loads(render_result.stdout)
    assert reminder["invoice_id"] == invoice_id
    assert "₪1,800.00" in reminder["body"]
