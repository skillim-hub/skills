from __future__ import annotations

import asyncio
import csv
import json
from datetime import date
from decimal import Decimal

import pytest
from click.testing import CliRunner

from domestic_bank_transfer_helper_cli import cli
from domestic_bank_transfer_helper_client import (
    RuntimeEnvironment,
    Severity,
    TransferMethod,
    TransferRequest,
    TransferValidationError,
    ValidationCode,
    async_validate_transfer,
    async_validate_transfers,
    build_bank_form_payload,
    create_transfer_record,
    format_ils,
    format_local_date,
    get_transfer_record,
    list_transfer_records,
    load_transfers_csv,
    normalize_account_number,
    normalize_bank_code,
    normalize_branch_code,
    normalize_digits,
    normalize_environment,
    parse_amount_ils,
    parse_value_date,
    record_payload,
    redact_account,
    recommend_transfer_method,
    request_from_mapping,
    state_file_path,
    validate_transfer,
    validate_transfers,
)


def make_request(**overrides):
    data = {
        "recipient_name": "Example Supplier Ltd",
        "bank_code": "12",
        "branch_code": "456",
        "account_number": "123456789",
        "amount_ils": "2450.80",
        "value_date": "03/06/2026",
        "purpose": "Invoice 1007",
        "reference": "INV-1007",
    }
    data.update(overrides)
    return TransferRequest(**data)


def test_normalize_digits_accepts_hebrew_and_arabic_indic_digits():
    assert normalize_digits("אב12٣٤") == "1234"


def test_normalize_bank_code_strips_leading_zeroes():
    assert normalize_bank_code("012") == "12"


def test_normalize_branch_code_pads_to_three_digits():
    assert normalize_branch_code("7") == "007"


def test_normalize_account_number_removes_separators():
    assert normalize_account_number("12-345 678") == "12345678"


def test_parse_amount_accepts_shekel_symbol_and_commas():
    assert parse_amount_ils("₪1,234.56") == Decimal("1234.56")


def test_parse_amount_rejects_text():
    assert parse_amount_ils("not money") is None


def test_parse_value_date_accepts_local_slash_format():
    assert parse_value_date("03/06/2026") == date(2026, 6, 3)


def test_parse_value_date_accepts_iso_format():
    assert parse_value_date("2026-06-03") == date(2026, 6, 3)


def test_format_ils_uses_shekel_symbol():
    assert format_ils("1234.5") == "₪1,234.50"


def test_format_local_date_uses_dd_mm_yyyy():
    assert format_local_date("2026-06-03") == "03/06/2026"


def test_masav_recommended_for_non_urgent_supplier_payment():
    report = validate_transfer(make_request(), today=date(2026, 6, 2))
    assert report.valid
    assert report.decision.method == TransferMethod.MASAV


def test_zahav_recommended_for_same_day_payment():
    report = validate_transfer(make_request(same_day=True), today=date(2026, 6, 2))
    assert report.decision.method == TransferMethod.ZAHAV


def test_zahav_recommended_for_high_value_payment():
    report = validate_transfer(make_request(amount_ils="1000000"), today=date(2026, 6, 2))
    assert report.decision.method == TransferMethod.ZAHAV


def test_explicit_masav_high_value_warns():
    report = validate_transfer(make_request(amount_ils="1000000", method="masav"), today=date(2026, 6, 2))
    assert any(issue.code == ValidationCode.HIGH_VALUE_MASAV for issue in report.warnings)


def test_missing_recipient_is_error():
    report = validate_transfer(make_request(recipient_name=""), today=date(2026, 6, 2))
    assert not report.valid
    assert any(issue.field == "recipient_name" for issue in report.errors)


def test_unknown_bank_is_warning_not_error():
    report = validate_transfer(make_request(bank_code="777"), today=date(2026, 6, 2))
    assert report.valid
    assert any(issue.code == ValidationCode.UNKNOWN_BANK_CODE for issue in report.warnings)


def test_known_bank_codes_match_bank_of_israel_identification_codes():
    report_9 = validate_transfer(make_request(bank_code="9"), today=date(2026, 6, 2))
    report_54 = validate_transfer(make_request(bank_code="54"), today=date(2026, 6, 2))
    assert report_9.normalized["bank_name"] == "D.I. Postal Finance Ltd"
    assert report_54.normalized["bank_name"] == "Bank of Jerusalem Ltd"


def test_invalid_branch_is_error():
    report = validate_transfer(make_request(branch_code="1234"), today=date(2026, 6, 2))
    assert not report.valid
    assert any(issue.code == ValidationCode.INVALID_BRANCH_CODE for issue in report.errors)


def test_short_branch_gets_padding_warning():
    report = validate_transfer(make_request(branch_code="7"), today=date(2026, 6, 2))
    assert any(issue.code == ValidationCode.BRANCH_PADDED for issue in report.warnings)
    assert report.normalized["branch_code"] == "007"


def test_invalid_account_is_error():
    report = validate_transfer(make_request(account_number="12"), today=date(2026, 6, 2))
    assert not report.valid
    assert any(issue.code == ValidationCode.INVALID_ACCOUNT_NUMBER for issue in report.errors)


def test_negative_amount_is_error():
    report = validate_transfer(make_request(amount_ils="-1"), today=date(2026, 6, 2))
    assert not report.valid
    assert any(issue.code == ValidationCode.INVALID_AMOUNT for issue in report.errors)


def test_past_date_is_error():
    report = validate_transfer(make_request(value_date="01/06/2026"), today=date(2026, 6, 2))
    assert not report.valid
    assert any(issue.code == ValidationCode.VALUE_DATE_PAST for issue in report.errors)


def test_friday_date_is_warning():
    report = validate_transfer(make_request(value_date="05/06/2026"), today=date(2026, 6, 2))
    assert any(issue.code == ValidationCode.VALUE_DATE_CALENDAR_CHECK for issue in report.warnings)


def test_empty_purpose_is_warning():
    report = validate_transfer(make_request(purpose=""), today=date(2026, 6, 2))
    assert any(issue.code == ValidationCode.PURPOSE_MISSING for issue in report.warnings)


def test_long_reference_is_warning():
    report = validate_transfer(make_request(reference="X" * 40), today=date(2026, 6, 2))
    assert any(issue.code == ValidationCode.REFERENCE_TOO_LONG for issue in report.warnings)


def test_production_high_value_requires_approval_warning():
    report = validate_transfer(make_request(amount_ils="60000"), today=date(2026, 6, 2), env="production")
    assert any(issue.code == ValidationCode.PRODUCTION_REQUIRES_APPROVAL for issue in report.warnings)


def test_build_payload_raises_for_errors():
    with pytest.raises(TransferValidationError):
        build_bank_form_payload(make_request(account_number="1"), today=date(2026, 6, 2))


def test_request_from_mapping_reads_common_fields():
    req = request_from_mapping({"recipient_name": "A", "bank_code": "12", "branch_code": "1", "account_number": "1234", "amount": "10", "urgent": "yes"})
    assert req.urgent is True
    assert req.amount_ils == "10"


def test_load_transfers_csv(tmp_path):
    path = tmp_path / "transfers.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["recipient_name", "bank_code", "branch_code", "account_number", "amount_ils"])
        writer.writeheader()
        writer.writerow({"recipient_name": "A", "bank_code": "12", "branch_code": "456", "account_number": "123456", "amount_ils": "10"})
    rows = load_transfers_csv(path)
    assert len(rows) == 1
    assert rows[0].recipient_name == "A"


def test_validate_transfers_returns_reports():
    reports = validate_transfers([make_request(), make_request(account_number="1")], today=date(2026, 6, 2))
    assert [report.valid for report in reports] == [True, False]


def test_async_validate_transfer():
    report = asyncio.run(async_validate_transfer(make_request(), today=date(2026, 6, 2)))
    assert report.valid


def test_async_validate_transfers():
    reports = asyncio.run(async_validate_transfers([make_request(), make_request()], today=date(2026, 6, 2)))
    assert len(reports) == 2
    assert all(report.valid for report in reports)


def test_redact_account_keeps_last_digits():
    assert redact_account("123456789") == "*****6789"


def test_recommend_transfer_method_bulk_uses_masav():
    decision = recommend_transfer_method(make_request(bulk_count=12))
    assert decision.method == TransferMethod.MASAV


def test_normalize_environment_accepts_valid_values():
    assert normalize_environment("sandbox") == RuntimeEnvironment.SANDBOX


def test_normalize_environment_rejects_invalid_values():
    with pytest.raises(ValueError):
        normalize_environment("qa")


def test_create_get_list_and_payload_record(tmp_path):
    record = create_transfer_record(make_request(), env="sandbox", storage_dir=tmp_path, today=date(2026, 6, 2))
    assert record["id"].startswith("dtf_")
    loaded = get_transfer_record(record["id"], env="sandbox", storage_dir=tmp_path)
    assert loaded["id"] == record["id"]
    assert list_transfer_records(env="sandbox", storage_dir=tmp_path)[0]["id"] == record["id"]
    payload = record_payload(record["id"], env="sandbox", storage_dir=tmp_path)
    assert payload["id"] == record["id"]
    assert state_file_path("sandbox", tmp_path).exists()


def test_record_payload_raises_for_invalid_record(tmp_path):
    record = create_transfer_record(make_request(account_number="1"), env="sandbox", storage_dir=tmp_path, today=date(2026, 6, 2))
    with pytest.raises(TransferValidationError):
        record_payload(record["id"], env="sandbox", storage_dir=tmp_path)


def test_cli_validate_json_success():
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--env", "sandbox",
            "validate",
            "--recipient-name", "Example Supplier Ltd",
            "--bank-code", "12",
            "--branch-code", "456",
            "--account-number", "123456789",
            "--amount-ils", "100",
            "--value-date", "03/06/2026",
            "--purpose", "Invoice",
            "--json-output",
        ],
    )
    assert result.exit_code == 0
    assert json.loads(result.output)["valid"] is True


def test_cli_create_show_payload_chain(tmp_path):
    runner = CliRunner()
    common = [
        "--env", "sandbox",
        "--state-dir", str(tmp_path),
    ]
    create_result = runner.invoke(
        cli,
        common
        + [
            "create",
            "--recipient-name", "Example Supplier Ltd",
            "--bank-code", "12",
            "--branch-code", "456",
            "--account-number", "123456789",
            "--amount-ils", "100",
            "--value-date", "03/06/2026",
            "--purpose", "Invoice",
        ],
    )
    assert create_result.exit_code == 0
    record_id = json.loads(create_result.output)["id"]
    show_result = runner.invoke(cli, common + ["show", record_id])
    assert show_result.exit_code == 0
    assert json.loads(show_result.output)["id"] == record_id
    payload_result = runner.invoke(cli, common + ["payload", record_id])
    assert payload_result.exit_code == 0
    assert json.loads(payload_result.output)["id"] == record_id


def test_cli_batch_summary(tmp_path):
    csv_path = tmp_path / "batch.csv"
    csv_path.write_text(
        "recipient_name,bank_code,branch_code,account_number,amount_ils,value_date,purpose\n"
        "A,12,456,123456,10,03/06/2026,Invoice\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(cli, ["--env", "sandbox", "batch", str(csv_path)])
    assert result.exit_code == 0
    assert "Valid: 1/1" in result.output
