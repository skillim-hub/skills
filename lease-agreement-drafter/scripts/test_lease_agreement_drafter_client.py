from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from lease_agreement_drafter import LeaseAgreementDrafterClient, ValidationError, build_request, load_request_file
from lease_agreement_drafter.client import covered_residential_lease, months_between, normalize_date, residential_deposit_cap


def base_request(**overrides):
    request = {
        "landlord": {"name": "דנה כהן", "id_number": "123456789"},
        "tenant": {"name": "נועם לוי", "id_number": "987654321"},
        "property": {"property_type": "apartment", "address": "הרצל 10", "city": "חיפה"},
        "terms": {"start_date": "01/08/2026", "end_date": "31/07/2027", "monthly_rent_ils": 5200, "security_deposit_ils": 10400},
        "language": "he",
    }
    for key, value in overrides.items():
        if isinstance(value, dict) and key in request:
            request[key].update(value)
        else:
            request[key] = value
    return request


def test_normalize_slash_date():
    assert normalize_date("01/08/2026") == "01/08/2026"


def test_normalize_dash_date():
    assert normalize_date("01-08-2026") == "01/08/2026"


def test_normalize_iso_date():
    assert normalize_date("2026-08-01") == "01/08/2026"


def test_invalid_date_raises():
    with pytest.raises(ValidationError):
        normalize_date("08.01.2026")


def test_months_between_positive():
    assert months_between("01/08/2026", "31/07/2027") > 11


def test_build_request_maps_nested_objects():
    req = build_request(base_request())
    assert req.landlord.name == "דנה כהן"
    assert req.property.property_type == "apartment"


def test_office_property_type_allowed():
    req = build_request(base_request(property={"property_type": "office", "permitted_use": "משרד"}))
    assert req.property.property_type == "office"


def test_invalid_property_type_rejected():
    with pytest.raises(ValidationError):
        build_request(base_request(property={"property_type": "warehouse"}))


def test_validate_clean_request_has_no_errors():
    client = LeaseAgreementDrafterClient()
    findings = client.validate(base_request())
    assert not [f for f in findings if f.severity == "error"]


def test_missing_tenant_name_error():
    client = LeaseAgreementDrafterClient()
    findings = client.validate(base_request(tenant={"name": ""}))
    assert any(f.code == "MISSING_PARTY_NAME" and f.severity == "error" for f in findings)


def test_missing_address_error():
    client = LeaseAgreementDrafterClient()
    findings = client.validate(base_request(property={"address": ""}))
    assert any(f.code == "MISSING_PROPERTY_ADDRESS" for f in findings)


def test_missing_rent_error():
    client = LeaseAgreementDrafterClient()
    findings = client.validate(base_request(terms={"monthly_rent_ils": 0}))
    assert any(f.code == "MISSING_RENT" for f in findings)


def test_invalid_range_error():
    client = LeaseAgreementDrafterClient()
    findings = client.validate(base_request(terms={"start_date": "01/08/2026", "end_date": "01/08/2026"}))
    assert any(f.code == "INVALID_DATE_RANGE" for f in findings)


def test_residential_lease_covered():
    assert covered_residential_lease(build_request(base_request())) is True


def test_short_residential_lease_not_covered():
    req = build_request(base_request(terms={"start_date": "01/08/2026", "end_date": "01/10/2026"}))
    assert covered_residential_lease(req) is False


def test_residential_cap_calculated():
    req = build_request(base_request())
    assert residential_deposit_cap(req) <= 15600


def test_residential_deposit_warning():
    client = LeaseAgreementDrafterClient()
    findings = client.validate(base_request(terms={"security_deposit_ils": 50000}))
    assert any(f.code == "RESIDENTIAL_DEPOSIT_CAP" for f in findings)


def test_vat_on_apartment_warning():
    client = LeaseAgreementDrafterClient()
    findings = client.validate(base_request(terms={"vat_applies": True}))
    assert any(f.code == "VAT_ON_APARTMENT" for f in findings)


def test_office_without_use_warning():
    client = LeaseAgreementDrafterClient()
    findings = client.validate(base_request(property={"property_type": "office", "permitted_use": ""}, terms={"vat_applies": True}))
    assert any(f.code == "OFFICE_WITHOUT_USE" for f in findings)


def test_draft_returns_id_and_markdown():
    client = LeaseAgreementDrafterClient(environment="sandbox")
    result = client.draft(base_request())
    assert result.id.startswith("lease_")
    assert "טיוטת הסכם" in result.markdown


def test_english_draft():
    client = LeaseAgreementDrafterClient()
    result = client.draft(base_request(language="en"))
    assert "Draft Lease Agreement" in result.markdown


def test_result_json_is_utf8():
    client = LeaseAgreementDrafterClient()
    result = client.draft(base_request())
    payload = json.loads(result.to_json())
    assert payload["title"].startswith("Apartment")


def test_scan_template_flags_missing_clauses():
    client = LeaseAgreementDrafterClient()
    findings = client.scan_template("שכר דירה ישולם בכל חודש")
    assert {f.code for f in findings} >= {"NO_REPAIR_CLAUSE", "NO_HANDOVER_PROTOCOL", "NO_EARLY_TERMINATION_BALANCE"}


def test_scan_template_passes_when_terms_present():
    client = LeaseAgreementDrafterClient()
    text = "תיקון פגם דחוף, פרוטוקול מסירה, סיום מוקדם בהודעה מוקדמת וזכות מקבילה"
    findings = client.scan_template(text)
    assert findings == []


def test_clause_index_extracts_headings():
    client = LeaseAgreementDrafterClient()
    result = client.draft(base_request())
    assert "צדדים" in client.render_clause_index(result)


def test_export_markdown(tmp_path: Path):
    client = LeaseAgreementDrafterClient()
    result = client.draft(base_request())
    output = client.export_markdown(result, tmp_path / "draft.md")
    assert output.read_text(encoding="utf-8").startswith("#")


def test_load_request_file(tmp_path: Path):
    path = tmp_path / "request.json"
    path.write_text(json.dumps(base_request(), ensure_ascii=False), encoding="utf-8")
    req = load_request_file(path)
    assert req.tenant.name == "נועם לוי"


def test_request_schema_contains_date_format():
    client = LeaseAgreementDrafterClient()
    assert client.request_schema()["date_format"] == "DD/MM/YYYY"


def test_error_catalog_contains_known_code():
    client = LeaseAgreementDrafterClient()
    assert "MISSING_RENT" in client.error_catalog()


def test_from_env(monkeypatch):
    monkeypatch.setenv("LEASE_DRAFTER_ENV", "production")
    monkeypatch.setenv("LEASE_DRAFTER_API_KEY", "token")
    client = LeaseAgreementDrafterClient.from_env()
    assert client.environment == "production"
    assert client.api_key == "token"


def test_invalid_env_rejected():
    with pytest.raises(ValidationError):
        LeaseAgreementDrafterClient(environment="demo")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_validate_async():
    client = LeaseAgreementDrafterClient()
    findings = await client.validate_async(base_request())
    assert isinstance(findings, list)


@pytest.mark.asyncio
async def test_draft_async():
    client = LeaseAgreementDrafterClient()
    result = await client.draft_async(base_request())
    assert result.id.startswith("lease_")


@pytest.mark.asyncio
async def test_scan_template_async():
    client = LeaseAgreementDrafterClient()
    findings = await client.scan_template_async("טקסט קצר")
    assert findings


def test_async_batch_without_pytest_marker():
    async def run():
        client = LeaseAgreementDrafterClient()
        return await client.draft_async(base_request())
    result = asyncio.run(run())
    assert result.status == "drafted"


def test_current_vat_rate_verified_constant():
    client = LeaseAgreementDrafterClient()
    assert client.current_vat_rate() == 0.18


def test_invoice_allocation_thresholds_2026():
    client = LeaseAgreementDrafterClient()
    assert client.invoice_allocation_thresholds()["from_2026_01_01"] == 10000
    assert client.invoice_allocation_thresholds()["from_2026_06_01"] == 5000


def test_ten_year_apartment_is_not_automatically_excluded():
    req = base_request()
    req["terms"]["start_date"] = "01/01/2026"
    req["terms"]["end_date"] = "31/12/2035"
    req["terms"]["monthly_rent_ils"] = 5000
    req["terms"]["security_deposit_ils"] = 25000
    findings = LeaseAgreementDrafterClient().validate(req)
    assert any(f.code == "RESIDENTIAL_DEPOSIT_CAP" for f in findings)
