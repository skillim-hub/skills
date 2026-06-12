"""Local claim tracker for Israeli health-insurance reimbursement workflows.

The module is intentionally offline-first. It stores claim records in a JSON file
so a freelancer, clinic administrator, small employer, or household can track
submissions without depending on a single insurer API.
"""

from __future__ import annotations

import asyncio
import csv
import json
import secrets
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from enum import Enum
from pathlib import Path
from typing import Any, Iterable, Literal, Optional


ILS_QUANT = Decimal("0.01")


class ClaimTrackerError(Exception):
    """Base exception for claim tracker failures."""


class ClaimNotFoundError(ClaimTrackerError):
    """Raised when a claim id is not present in the store."""


class ValidationError(ClaimTrackerError):
    """Raised when claim input is invalid."""


class ClaimStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    MISSING_DOCUMENTS = "missing_documents"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    PARTIALLY_APPROVED = "partially_approved"
    REJECTED = "rejected"
    APPEALED = "appealed"
    PAID = "paid"
    CLOSED = "closed"


class PolicyType(str, Enum):
    SUPPLEMENTARY = "supplementary"
    PRIVATE = "private"
    NATIONAL = "national"
    OTHER = "other"


def money(value: Decimal | int | float | str) -> Decimal:
    """Return an Israeli shekel amount rounded to two decimals."""
    try:
        amount = Decimal(str(value)).quantize(ILS_QUANT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError) as exc:
        raise ValidationError(f"Invalid amount: {value!r}") from exc
    return amount


def parse_israeli_date(value: date | str) -> date:
    """Parse ISO, DD/MM/YYYY, or DD-MM-YYYY dates."""
    if isinstance(value, date):
        return value
    if not isinstance(value, str) or not value.strip():
        raise ValidationError("Date must be a non-empty string or date object")
    clean = value.strip()
    formats = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y")
    for fmt in formats:
        try:
            return datetime.strptime(clean, fmt).date()
        except ValueError:
            pass
    raise ValidationError(f"Unsupported date format: {value!r}")


def format_israeli_date(value: date | str | None) -> str:
    """Format a date as DD/MM/YYYY."""
    if value is None:
        return ""
    return parse_israeli_date(value).strftime("%d/%m/%Y")


def format_ils(value: Decimal | int | float | str) -> str:
    """Format a value as Israeli shekels."""
    return f"₪{money(value):,.2f}"


def _today() -> date:
    return date.today()


def _coerce_policy_type(value: PolicyType | str) -> PolicyType:
    if isinstance(value, PolicyType):
        return value
    return PolicyType(str(value))


def _coerce_claim_status(value: ClaimStatus | str) -> ClaimStatus:
    if isinstance(value, ClaimStatus):
        return value
    return ClaimStatus(str(value))


def _utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class Document:
    name: str
    document_type: str
    received: bool = True
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "document_type": self.document_type,
            "received": self.received,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Document":
        return cls(
            name=str(data.get("name", "")),
            document_type=str(data.get("document_type", "")),
            received=bool(data.get("received", True)),
            notes=str(data.get("notes", "")),
        )


@dataclass(slots=True)
class Reimbursement:
    amount_ils: Decimal
    paid_date: date
    payer: str
    reference: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "amount_ils": str(money(self.amount_ils)),
            "paid_date": self.paid_date.isoformat(),
            "payer": self.payer,
            "reference": self.reference,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Reimbursement":
        return cls(
            amount_ils=money(data.get("amount_ils", "0")),
            paid_date=parse_israeli_date(data.get("paid_date", "")),
            payer=str(data.get("payer", "")),
            reference=str(data.get("reference", "")),
        )


@dataclass(slots=True)
class TimelineEvent:
    at: datetime
    status: str
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"at": self.at.isoformat(timespec="seconds"), "status": self.status, "note": self.note}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TimelineEvent":
        raw = str(data.get("at") or _utc_now().isoformat(timespec="seconds"))
        try:
            at = datetime.fromisoformat(raw)
        except ValueError:
            at = _utc_now()
        return cls(at=at, status=str(data.get("status", "")), note=str(data.get("note", "")))


@dataclass(slots=True)
class Claim:
    id: str
    claimant_reference: str
    policy_type: PolicyType
    provider: str
    service_date: date
    submission_date: date
    amount_claimed_ils: Decimal
    description: str
    status: ClaimStatus = ClaimStatus.DRAFT
    channel: str = ""
    policy_number_last4: str = ""
    service_kind: str = ""
    documents: list[Document] = field(default_factory=list)
    reimbursements: list[Reimbursement] = field(default_factory=list)
    timeline: list[TimelineEvent] = field(default_factory=list)
    follow_up_date: date | None = None
    notes: str = ""
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=_utc_now)
    updated_at: datetime = field(default_factory=_utc_now)

    def total_reimbursed_ils(self) -> Decimal:
        return sum((money(item.amount_ils) for item in self.reimbursements), Decimal("0.00")).quantize(ILS_QUANT)

    def reimbursement_gap_ils(self) -> Decimal:
        return (money(self.amount_claimed_ils) - self.total_reimbursed_ils()).quantize(ILS_QUANT)

    def is_overdue(self, as_of: date | None = None) -> bool:
        if self.follow_up_date is None:
            return False
        return self.status not in {ClaimStatus.PAID, ClaimStatus.CLOSED} and self.follow_up_date < (as_of or _today())

    def missing_documents(self) -> list[str]:
        supplied = {doc.document_type.strip().lower() for doc in self.documents if doc.received}
        required = set(required_documents(self.policy_type, self.service_kind))
        return sorted(doc for doc in required if doc.lower() not in supplied)

    def to_dict(self, *, redact: bool = False) -> dict[str, Any]:
        claimant_reference = self.claimant_reference
        if redact and len(claimant_reference) > 4:
            claimant_reference = f"***{claimant_reference[-4:]}"
        return {
            "id": self.id,
            "claimant_reference": claimant_reference,
            "policy_type": self.policy_type.value,
            "provider": self.provider,
            "service_date": self.service_date.isoformat(),
            "submission_date": self.submission_date.isoformat(),
            "amount_claimed_ils": str(money(self.amount_claimed_ils)),
            "description": self.description,
            "status": self.status.value,
            "channel": self.channel,
            "policy_number_last4": self.policy_number_last4,
            "service_kind": self.service_kind,
            "documents": [doc.to_dict() for doc in self.documents],
            "reimbursements": [item.to_dict() for item in self.reimbursements],
            "timeline": [event.to_dict() for event in self.timeline],
            "follow_up_date": self.follow_up_date.isoformat() if self.follow_up_date else None,
            "notes": self.notes,
            "tags": list(self.tags),
            "created_at": self.created_at.isoformat(timespec="seconds"),
            "updated_at": self.updated_at.isoformat(timespec="seconds"),
            "total_reimbursed_ils": str(self.total_reimbursed_ils()),
            "reimbursement_gap_ils": str(self.reimbursement_gap_ils()),
            "missing_documents": self.missing_documents(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Claim":
        return cls(
            id=str(data["id"]),
            claimant_reference=str(data.get("claimant_reference", "")),
            policy_type=_coerce_policy_type(data.get("policy_type", PolicyType.OTHER.value)),
            provider=str(data.get("provider", "")),
            service_date=parse_israeli_date(data.get("service_date", "")),
            submission_date=parse_israeli_date(data.get("submission_date", "")),
            amount_claimed_ils=money(data.get("amount_claimed_ils", "0")),
            description=str(data.get("description", "")),
            status=_coerce_claim_status(data.get("status", ClaimStatus.DRAFT.value)),
            channel=str(data.get("channel", "")),
            policy_number_last4=str(data.get("policy_number_last4", "")),
            service_kind=str(data.get("service_kind", "")),
            documents=[Document.from_dict(item) for item in data.get("documents", [])],
            reimbursements=[Reimbursement.from_dict(item) for item in data.get("reimbursements", [])],
            timeline=[TimelineEvent.from_dict(item) for item in data.get("timeline", [])],
            follow_up_date=parse_israeli_date(data["follow_up_date"]) if data.get("follow_up_date") else None,
            notes=str(data.get("notes", "")),
            tags=list(data.get("tags", [])),
            created_at=datetime.fromisoformat(str(data.get("created_at"))) if data.get("created_at") else _utc_now(),
            updated_at=datetime.fromisoformat(str(data.get("updated_at"))) if data.get("updated_at") else _utc_now(),
        )


def required_documents(policy_type: PolicyType | str, service_kind: str = "") -> list[str]:
    """Return typical document checklist items for an Israeli health claim."""
    policy = _coerce_policy_type(policy_type)
    kind = service_kind.strip().lower()
    docs = ["tax_invoice_or_receipt", "medical_referral_or_summary", "payment_proof"]
    if policy == PolicyType.PRIVATE:
        docs.extend(["policy_clause_reference", "claim_form"])
    if policy == PolicyType.SUPPLEMENTARY:
        docs.extend(["kupat_holim_member_number", "supplementary_plan_level"])
    if "surgery" in kind or "ניתוח" in kind:
        docs.extend(["hospital_discharge_summary", "procedure_report"])
    if "consult" in kind or "ייעוץ" in kind:
        docs.append("specialist_license_or_provider_details")
    if "medication" in kind or "תרופה" in kind:
        docs.extend(["prescription", "pharmacy_receipt"])
    return sorted(set(docs))


class HealthInsuranceClaimTrackerClient:
    """Typed synchronous client for local claim tracking."""

    def __init__(self, storage_path: str | Path | None = None, *, clock: Any | None = None) -> None:
        self.storage_path = Path(storage_path).expanduser() if storage_path else Path.home() / ".hict" / "claims.json"
        self.clock = clock or _today
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._write_payload({"claims": []})

    def create_claim(
        self,
        *,
        claimant_reference: str,
        policy_type: PolicyType | str,
        provider: str,
        service_date: date | str,
        submission_date: date | str,
        amount_claimed_ils: Decimal | int | float | str,
        description: str,
        status: ClaimStatus | str = ClaimStatus.SUBMITTED,
        channel: str = "",
        policy_number_last4: str = "",
        service_kind: str = "",
        notes: str = "",
        tags: Iterable[str] = (),
        follow_up_date: date | str | None = None,
    ) -> Claim:
        claim = Claim(
            id=self._new_id(),
            claimant_reference=claimant_reference.strip(),
            policy_type=_coerce_policy_type(policy_type),
            provider=provider.strip(),
            service_date=parse_israeli_date(service_date),
            submission_date=parse_israeli_date(submission_date),
            amount_claimed_ils=money(amount_claimed_ils),
            description=description.strip(),
            status=_coerce_claim_status(status),
            channel=channel.strip(),
            policy_number_last4=policy_number_last4.strip()[-4:],
            service_kind=service_kind.strip(),
            notes=notes.strip(),
            tags=[tag.strip() for tag in tags if str(tag).strip()],
            follow_up_date=parse_israeli_date(follow_up_date) if follow_up_date else None,
        )
        errors = self.validate_claim(claim)
        if errors:
            raise ValidationError("; ".join(errors))
        claim.timeline.append(TimelineEvent(_utc_now(), claim.status.value, "claim created"))
        self._upsert(claim)
        return claim

    def get_claim(self, claim_id: str) -> Claim:
        for claim in self._read_claims():
            if claim.id == claim_id:
                return claim
        raise ClaimNotFoundError(f"Claim not found: {claim_id}")

    def list_claims(
        self,
        *,
        status: ClaimStatus | str | None = None,
        provider: str | None = None,
        policy_type: PolicyType | str | None = None,
        overdue_only: bool = False,
        as_of: date | str | None = None,
    ) -> list[Claim]:
        claims = self._read_claims()
        if status:
            wanted = _coerce_claim_status(status)
            claims = [claim for claim in claims if claim.status == wanted]
        if provider:
            claims = [claim for claim in claims if claim.provider.lower() == provider.lower()]
        if policy_type:
            wanted_policy = _coerce_policy_type(policy_type)
            claims = [claim for claim in claims if claim.policy_type == wanted_policy]
        if overdue_only:
            check_date = parse_israeli_date(as_of) if as_of else self.clock()
            claims = [claim for claim in claims if claim.is_overdue(check_date)]
        return sorted(claims, key=lambda item: (item.submission_date, item.id))

    def update_claim_status(self, claim_id: str, status: ClaimStatus | str, *, note: str = "") -> Claim:
        claim = self.get_claim(claim_id)
        claim.status = _coerce_claim_status(status)
        claim.updated_at = _utc_now()
        claim.timeline.append(TimelineEvent(_utc_now(), claim.status.value, note.strip()))
        self._upsert(claim)
        return claim

    def add_document(
        self,
        claim_id: str,
        *,
        name: str,
        document_type: str,
        received: bool = True,
        notes: str = "",
    ) -> Claim:
        if not name.strip() or not document_type.strip():
            raise ValidationError("Document name and document_type are required")
        claim = self.get_claim(claim_id)
        claim.documents.append(Document(name=name.strip(), document_type=document_type.strip(), received=received, notes=notes.strip()))
        claim.updated_at = _utc_now()
        claim.timeline.append(TimelineEvent(_utc_now(), "document", document_type.strip()))
        self._upsert(claim)
        return claim

    def add_reimbursement(
        self,
        claim_id: str,
        *,
        amount_ils: Decimal | int | float | str,
        paid_date: date | str,
        payer: str,
        reference: str = "",
    ) -> Claim:
        amount = money(amount_ils)
        if amount <= 0:
            raise ValidationError("Reimbursement amount must be positive")
        if not payer.strip():
            raise ValidationError("Payer is required")
        claim = self.get_claim(claim_id)
        claim.reimbursements.append(
            Reimbursement(amount_ils=amount, paid_date=parse_israeli_date(paid_date), payer=payer.strip(), reference=reference.strip())
        )
        claim.updated_at = _utc_now()
        if claim.reimbursement_gap_ils() <= Decimal("0.00"):
            claim.status = ClaimStatus.PAID
        claim.timeline.append(TimelineEvent(_utc_now(), "reimbursement", f"{payer.strip()} {format_ils(amount)}"))
        self._upsert(claim)
        return claim

    def set_follow_up(self, claim_id: str, follow_up_date: date | str) -> Claim:
        claim = self.get_claim(claim_id)
        claim.follow_up_date = parse_israeli_date(follow_up_date)
        claim.updated_at = _utc_now()
        claim.timeline.append(TimelineEvent(_utc_now(), "follow_up", claim.follow_up_date.isoformat()))
        self._upsert(claim)
        return claim

    def reimbursement_gap(self, claim_id: str) -> Decimal:
        return self.get_claim(claim_id).reimbursement_gap_ils()

    def overdue_claims(self, *, as_of: date | str | None = None) -> list[Claim]:
        check_date = parse_israeli_date(as_of) if as_of else self.clock()
        return self.list_claims(overdue_only=True, as_of=check_date)

    def summary(self) -> dict[str, Any]:
        claims = self._read_claims()
        by_status: dict[str, int] = {}
        total_claimed = Decimal("0.00")
        total_reimbursed = Decimal("0.00")
        for claim in claims:
            by_status[claim.status.value] = by_status.get(claim.status.value, 0) + 1
            total_claimed += money(claim.amount_claimed_ils)
            total_reimbursed += claim.total_reimbursed_ils()
        return {
            "claim_count": len(claims),
            "by_status": dict(sorted(by_status.items())),
            "total_claimed_ils": str(money(total_claimed)),
            "total_reimbursed_ils": str(money(total_reimbursed)),
            "open_gap_ils": str(money(total_claimed - total_reimbursed)),
        }

    def export_csv(self, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        rows = [claim.to_dict() for claim in self._read_claims()]
        fields = [
            "id",
            "claimant_reference",
            "policy_type",
            "provider",
            "service_date",
            "submission_date",
            "amount_claimed_ils",
            "status",
            "channel",
            "policy_number_last4",
            "service_kind",
            "description",
            "follow_up_date",
            "notes",
            "tags",
            "total_reimbursed_ils",
            "reimbursement_gap_ils",
        ]
        with output.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for row in rows:
                flat = {key: row.get(key, "") for key in fields}
                flat["tags"] = ",".join(row.get("tags", []))
                writer.writerow(flat)
        return output

    def import_csv(self, path: str | Path) -> list[Claim]:
        imported: list[Claim] = []
        with Path(path).open("r", newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                claim = Claim(
                    id=row.get("id") or self._new_id(),
                    claimant_reference=row.get("claimant_reference", ""),
                    policy_type=_coerce_policy_type(row.get("policy_type") or PolicyType.OTHER.value),
                    provider=row.get("provider", ""),
                    service_date=parse_israeli_date(row.get("service_date", "")),
                    submission_date=parse_israeli_date(row.get("submission_date", "")),
                    amount_claimed_ils=money(row.get("amount_claimed_ils", "0")),
                    status=_coerce_claim_status(row.get("status") or ClaimStatus.SUBMITTED.value),
                    channel=row.get("channel", ""),
                    policy_number_last4=row.get("policy_number_last4", ""),
                    service_kind=row.get("service_kind", ""),
                    description=row.get("description", ""),
                    follow_up_date=parse_israeli_date(row["follow_up_date"]) if row.get("follow_up_date") else None,
                    notes=row.get("notes", ""),
                    tags=[tag for tag in row.get("tags", "").split(",") if tag],
                )
                self._upsert(claim)
                imported.append(claim)
        return imported

    def export_json(self, path: str | Path, *, redact: bool = False) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        payload = {"claims": [claim.to_dict(redact=redact) for claim in self._read_claims()]}
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return output

    def validate_claim(self, claim: Claim) -> list[str]:
        errors: list[str] = []
        if not claim.claimant_reference.strip():
            errors.append("claimant_reference is required")
        if not claim.provider.strip():
            errors.append("provider is required")
        if not claim.description.strip():
            errors.append("description is required")
        if claim.amount_claimed_ils <= 0:
            errors.append("amount_claimed_ils must be positive")
        if claim.submission_date < claim.service_date:
            errors.append("submission_date cannot be before service_date")
        if claim.service_date > self.clock():
            errors.append("service_date cannot be in the future")
        if claim.policy_number_last4 and not claim.policy_number_last4.isdigit():
            errors.append("policy_number_last4 must contain only digits")
        return errors

    def _new_id(self) -> str:
        return f"HICT-{_utc_now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"

    def _read_payload(self) -> dict[str, Any]:
        try:
            return json.loads(self.storage_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {"claims": []}
        except json.JSONDecodeError as exc:
            raise ClaimTrackerError(f"Storage file is not valid JSON: {self.storage_path}") from exc

    def _write_payload(self, payload: dict[str, Any]) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(self.storage_path.parent), delete=False) as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            temp_name = handle.name
        Path(temp_name).replace(self.storage_path)

    def _read_claims(self) -> list[Claim]:
        payload = self._read_payload()
        return [Claim.from_dict(item) for item in payload.get("claims", [])]

    def _upsert(self, claim: Claim) -> None:
        claims = self._read_claims()
        replaced = False
        for index, existing in enumerate(claims):
            if existing.id == claim.id:
                claims[index] = claim
                replaced = True
                break
        if not replaced:
            claims.append(claim)
        payload = {"claims": [item.to_dict() for item in sorted(claims, key=lambda item: item.id)]}
        self._write_payload(payload)


class AsyncHealthInsuranceClaimTrackerClient:
    """Async facade for the local claim tracker."""

    def __init__(self, storage_path: str | Path | None = None, *, clock: Any | None = None) -> None:
        self._client = HealthInsuranceClaimTrackerClient(storage_path=storage_path, clock=clock)

    async def create_claim(self, **kwargs: Any) -> Claim:
        return await asyncio.to_thread(self._client.create_claim, **kwargs)

    async def get_claim(self, claim_id: str) -> Claim:
        return await asyncio.to_thread(self._client.get_claim, claim_id)

    async def list_claims(self, **kwargs: Any) -> list[Claim]:
        return await asyncio.to_thread(self._client.list_claims, **kwargs)

    async def update_claim_status(self, claim_id: str, status: ClaimStatus | str, *, note: str = "") -> Claim:
        return await asyncio.to_thread(self._client.update_claim_status, claim_id, status, note=note)

    async def add_document(self, claim_id: str, **kwargs: Any) -> Claim:
        return await asyncio.to_thread(self._client.add_document, claim_id, **kwargs)

    async def add_reimbursement(self, claim_id: str, **kwargs: Any) -> Claim:
        return await asyncio.to_thread(self._client.add_reimbursement, claim_id, **kwargs)

    async def set_follow_up(self, claim_id: str, follow_up_date: date | str) -> Claim:
        return await asyncio.to_thread(self._client.set_follow_up, claim_id, follow_up_date)

    async def overdue_claims(self, **kwargs: Any) -> list[Claim]:
        return await asyncio.to_thread(self._client.overdue_claims, **kwargs)

    async def summary(self) -> dict[str, Any]:
        return await asyncio.to_thread(self._client.summary)

    async def close(self) -> None:
        return None


__all__ = [
    "AsyncHealthInsuranceClaimTrackerClient",
    "Claim",
    "ClaimNotFoundError",
    "ClaimStatus",
    "ClaimTrackerError",
    "Document",
    "HealthInsuranceClaimTrackerClient",
    "PolicyType",
    "Reimbursement",
    "TimelineEvent",
    "ValidationError",
    "format_ils",
    "format_israeli_date",
    "money",
    "parse_israeli_date",
    "required_documents",
]
