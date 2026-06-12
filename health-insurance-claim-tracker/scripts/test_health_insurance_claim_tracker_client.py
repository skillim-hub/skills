from __future__ import annotations

import csv
import json
from datetime import date
from decimal import Decimal

import pytest

from health_insurance_claim_tracker import (
    AsyncHealthInsuranceClaimTrackerClient,
    ClaimNotFoundError,
    ClaimStatus,
    HealthInsuranceClaimTrackerClient,
    PolicyType,
    ValidationError,
    format_ils,
    format_israeli_date,
    money,
    parse_israeli_date,
    required_documents,
)


def make_client(tmp_path, today=date(2026, 6, 4)):
    return HealthInsuranceClaimTrackerClient(tmp_path / "claims.json", clock=lambda: today)


def make_claim(client):
    return client.create_claim(
        claimant_reference="client-123456789",
        policy_type=PolicyType.PRIVATE,
        provider="Example Insurance",
        service_date="01/05/2026",
        submission_date="15/05/2026",
        amount_claimed_ils="1200.50",
        description="Specialist consultation reimbursement",
        channel="online portal",
        policy_number_last4="7788",
        service_kind="consultation",
        follow_up_date="01/06/2026",
        tags=["consultation", "private"],
    )


def test_create_claim_persists_to_disk(tmp_path):
    client = make_client(tmp_path)
    claim = make_claim(client)
    assert claim.id.startswith("HICT-")
    assert (tmp_path / "claims.json").exists()
    reloaded = make_client(tmp_path).get_claim(claim.id)
    assert reloaded.provider == "Example Insurance"


def test_missing_claim_raises(tmp_path):
    client = make_client(tmp_path)
    with pytest.raises(ClaimNotFoundError):
        client.get_claim("missing")


def test_money_rounds_to_two_decimals():
    assert money("10.555") == Decimal("10.56")


def test_format_ils():
    assert format_ils("1234.5") == "₪1,234.50"


def test_parse_iso_date():
    assert parse_israeli_date("2026-05-31") == date(2026, 5, 31)


def test_parse_slash_date():
    assert parse_israeli_date("31/05/2026") == date(2026, 5, 31)


def test_parse_dash_israeli_date():
    assert parse_israeli_date("31-05-2026") == date(2026, 5, 31)


def test_parse_bad_date_raises():
    with pytest.raises(ValidationError):
        parse_israeli_date("31.05.2026")


def test_format_israeli_date():
    assert format_israeli_date("2026-05-31") == "31/05/2026"


def test_create_claim_rejects_future_service_date(tmp_path):
    client = make_client(tmp_path, today=date(2026, 6, 4))
    with pytest.raises(ValidationError):
        client.create_claim(
            claimant_reference="abc",
            policy_type="private",
            provider="Insurer",
            service_date="05/06/2026",
            submission_date="06/06/2026",
            amount_claimed_ils="10",
            description="Future service",
        )


def test_create_claim_rejects_submission_before_service(tmp_path):
    client = make_client(tmp_path)
    with pytest.raises(ValidationError):
        client.create_claim(
            claimant_reference="abc",
            policy_type="private",
            provider="Insurer",
            service_date="05/05/2026",
            submission_date="04/05/2026",
            amount_claimed_ils="10",
            description="Bad date order",
        )


def test_create_claim_rejects_bad_policy_last4(tmp_path):
    client = make_client(tmp_path)
    with pytest.raises(ValidationError):
        client.create_claim(
            claimant_reference="abc",
            policy_type="private",
            provider="Insurer",
            service_date="03/05/2026",
            submission_date="04/05/2026",
            amount_claimed_ils="10",
            description="Bad policy",
            policy_number_last4="77A8",
        )


def test_list_claims_by_status(tmp_path):
    client = make_client(tmp_path)
    claim = make_claim(client)
    client.update_claim_status(claim.id, ClaimStatus.IN_REVIEW)
    assert [item.id for item in client.list_claims(status="in_review")] == [claim.id]


def test_list_claims_by_provider(tmp_path):
    client = make_client(tmp_path)
    claim = make_claim(client)
    assert [item.id for item in client.list_claims(provider="example insurance")] == [claim.id]


def test_add_document_reduces_missing_documents(tmp_path):
    client = make_client(tmp_path)
    claim = make_claim(client)
    before = set(claim.missing_documents())
    assert "claim_form" in before
    updated = client.add_document(claim.id, name="claim.pdf", document_type="claim_form")
    after = set(updated.missing_documents())
    assert "claim_form" not in after


def test_add_document_requires_name(tmp_path):
    client = make_client(tmp_path)
    claim = make_claim(client)
    with pytest.raises(ValidationError):
        client.add_document(claim.id, name="", document_type="claim_form")


def test_required_documents_private_consultation():
    docs = required_documents(PolicyType.PRIVATE, "consultation")
    assert "claim_form" in docs
    assert "specialist_license_or_provider_details" in docs


def test_required_documents_supplementary_medication():
    docs = required_documents("supplementary", "medication")
    assert "pharmacy_receipt" in docs
    assert "kupat_holim_member_number" in docs


def test_add_reimbursement_updates_gap(tmp_path):
    client = make_client(tmp_path)
    claim = make_claim(client)
    updated = client.add_reimbursement(claim.id, amount_ils="200.50", paid_date="20/05/2026", payer="Example Insurance")
    assert updated.reimbursement_gap_ils() == Decimal("1000.00")


def test_full_reimbursement_sets_paid(tmp_path):
    client = make_client(tmp_path)
    claim = make_claim(client)
    updated = client.add_reimbursement(claim.id, amount_ils="1200.50", paid_date="20/05/2026", payer="Example Insurance")
    assert updated.status == ClaimStatus.PAID


def test_negative_reimbursement_rejected(tmp_path):
    client = make_client(tmp_path)
    claim = make_claim(client)
    with pytest.raises(ValidationError):
        client.add_reimbursement(claim.id, amount_ils="-1", paid_date="20/05/2026", payer="Example Insurance")


def test_overdue_claims(tmp_path):
    client = make_client(tmp_path, today=date(2026, 6, 4))
    claim = make_claim(client)
    assert [item.id for item in client.overdue_claims()] == [claim.id]


def test_paid_claim_not_overdue(tmp_path):
    client = make_client(tmp_path, today=date(2026, 6, 4))
    claim = make_claim(client)
    client.add_reimbursement(claim.id, amount_ils="1200.50", paid_date="20/05/2026", payer="Example Insurance")
    assert client.overdue_claims() == []


def test_set_follow_up(tmp_path):
    client = make_client(tmp_path)
    claim = make_claim(client)
    updated = client.set_follow_up(claim.id, "10/06/2026")
    assert format_israeli_date(updated.follow_up_date) == "10/06/2026"


def test_summary_totals(tmp_path):
    client = make_client(tmp_path)
    claim = make_claim(client)
    client.add_reimbursement(claim.id, amount_ils="200.50", paid_date="20/05/2026", payer="Example Insurance")
    summary = client.summary()
    assert summary["claim_count"] == 1
    assert summary["total_claimed_ils"] == "1200.50"
    assert summary["total_reimbursed_ils"] == "200.50"
    assert summary["open_gap_ils"] == "1000.00"


def test_export_csv(tmp_path):
    client = make_client(tmp_path)
    claim = make_claim(client)
    output = client.export_csv(tmp_path / "claims.csv")
    rows = list(csv.DictReader(output.open(encoding="utf-8")))
    assert rows[0]["id"] == claim.id
    assert rows[0]["amount_claimed_ils"] == "1200.50"


def test_import_csv(tmp_path):
    source = tmp_path / "source.csv"
    source.write_text(
        "id,claimant_reference,policy_type,provider,service_date,submission_date,amount_claimed_ils,status,channel,policy_number_last4,service_kind,description,follow_up_date,notes,tags,total_reimbursed_ils,reimbursement_gap_ils\n"
        "CLAIM-1,ref,private,Insurer,2026-05-01,2026-05-02,300.00,submitted,portal,1234,consultation,Imported claim,2026-06-01,note,tag,0,300\n",
        encoding="utf-8",
    )
    client = make_client(tmp_path)
    imported = client.import_csv(source)
    assert imported[0].id == "CLAIM-1"
    assert client.get_claim("CLAIM-1").provider == "Insurer"


def test_export_json_redacts_claimant_reference(tmp_path):
    client = make_client(tmp_path)
    make_claim(client)
    output = client.export_json(tmp_path / "redacted.json", redact=True)
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["claims"][0]["claimant_reference"].startswith("***")


def test_to_dict_contains_derived_fields(tmp_path):
    client = make_client(tmp_path)
    claim = make_claim(client)
    data = claim.to_dict()
    assert "missing_documents" in data
    assert data["reimbursement_gap_ils"] == "1200.50"


@pytest.mark.asyncio
async def test_async_create_and_get(tmp_path):
    client = AsyncHealthInsuranceClaimTrackerClient(tmp_path / "claims.json", clock=lambda: date(2026, 6, 4))
    claim = await client.create_claim(
        claimant_reference="async-ref",
        policy_type="private",
        provider="Async Insurance",
        service_date="01/05/2026",
        submission_date="15/05/2026",
        amount_claimed_ils="90",
        description="Async claim",
    )
    fetched = await client.get_claim(claim.id)
    assert fetched.provider == "Async Insurance"


@pytest.mark.asyncio
async def test_async_summary(tmp_path):
    client = AsyncHealthInsuranceClaimTrackerClient(tmp_path / "claims.json", clock=lambda: date(2026, 6, 4))
    await client.create_claim(
        claimant_reference="async-ref",
        policy_type="supplementary",
        provider="Kupat Holim",
        service_date="01/05/2026",
        submission_date="15/05/2026",
        amount_claimed_ils="90",
        description="Async claim",
    )
    summary = await client.summary()
    assert summary["claim_count"] == 1


def test_public_import_from_package():
    from health_insurance_claim_tracker import HealthInsuranceClaimTrackerClient as Imported

    assert Imported is HealthInsuranceClaimTrackerClient
