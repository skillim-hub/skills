from __future__ import annotations

import asyncio
import csv
import hashlib
import hmac
import json
import re
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, Mapping, Optional, Sequence


ILS = Decimal("1.00")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ReferralProgramError(Exception):
    pass


class ValidationError(ReferralProgramError):
    pass


class DuplicateReferralError(ReferralProgramError):
    pass


class GatewayError(ReferralProgramError):
    pass


class RewardType(str, Enum):
    CREDIT = "credit"
    COUPON = "coupon"
    CASH = "cash"
    REFUND = "refund"
    GIFT_CARD = "gift_card"
    DONATION = "donation"


class ReferralStatus(str, Enum):
    INVITED = "invited"
    REGISTERED = "registered"
    QUALIFIED = "qualified"
    REWARD_PENDING = "reward_pending"
    FRAUD_REVIEW = "fraud_review"
    REJECTED = "rejected"
    REVERSED = "reversed"


class RewardStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    PAID = "paid"
    REVERSED = "reversed"
    EXPIRED = "expired"


@dataclass
class Customer:
    customer_id: str
    name: str
    email: str
    phone: str
    consent_marketing: bool = False
    created_at: str = field(default_factory=lambda: now_iso())
    is_existing_customer: bool = False
    is_employee: bool = False
    vat_or_id: Optional[str] = None
    bank_account: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReferralProgram:
    program_id: str
    name: str
    reward_type: RewardType
    reward_amount_ils: Decimal
    qualifying_action: str
    cooldown_days: int = 14
    max_rewards_per_customer: int = 5
    minimum_order_ils: Decimal = Decimal("0.00")
    terms_version: str = "v1"
    active: bool = True
    require_tax_document_for_cash: bool = True
    created_at: str = field(default_factory=lambda: now_iso())


@dataclass
class ReferralEvent:
    event_id: str
    program_id: str
    referrer_id: str
    referred_customer_id: str
    source: str
    referral_code: str
    status: ReferralStatus = ReferralStatus.REGISTERED
    created_at: str = field(default_factory=lambda: now_iso())
    qualified_at: Optional[str] = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    fraud_score: int = 0
    review_reason: Optional[str] = None
    terms_version: str = "v1"


@dataclass
class Reward:
    reward_id: str
    event_id: str
    recipient_customer_id: str
    amount_ils: Decimal
    reward_type: RewardType
    status: RewardStatus = RewardStatus.PENDING
    tax_treatment: str = "unclassified"
    gateway: Optional[str] = None
    gateway_reference: Optional[str] = None
    idempotency_key: Optional[str] = None
    document_number: Optional[str] = None
    created_at: str = field(default_factory=lambda: now_iso())
    approved_at: Optional[str] = None
    paid_at: Optional[str] = None
    expires_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditEntry:
    timestamp: str
    actor: str
    action: str
    entity_id: str
    before: Dict[str, Any]
    after: Dict[str, Any]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def money(value: Decimal | int | float | str) -> Decimal:
    return Decimal(str(value)).quantize(ILS, rounding=ROUND_HALF_UP)


def normalize_email(email: str) -> str:
    email = email.strip().lower()
    if not EMAIL_RE.match(email):
        raise ValidationError(f"Invalid email: {email}")
    return email


def normalize_israeli_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    if digits.startswith("972"):
        digits = digits[3:]
    if digits.startswith("0"):
        digits = digits[1:]
    if not digits.startswith("5") or len(digits) != 9:
        raise ValidationError(f"Invalid Israeli mobile phone: {phone}")
    return "+972" + digits


def validate_israeli_phone(phone: str) -> bool:
    try:
        normalize_israeli_phone(phone)
        return True
    except ValidationError:
        return False


def validate_israeli_id(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    if not digits or len(digits) > 9:
        return False
    digits = digits.zfill(9)
    total = 0
    for index, char in enumerate(digits):
        step = int(char) * (1 if index % 2 == 0 else 2)
        total += step if step < 10 else step - 9
    return total % 10 == 0


def parse_dd_mm_yyyy(value: str) -> date:
    try:
        return datetime.strptime(value, "%d-%m-%Y").date()
    except ValueError as exc:
        raise ValidationError(f"Expected DD-MM-YYYY date, got {value!r}") from exc


def format_dd_mm_yyyy(value: date | datetime) -> str:
    if isinstance(value, datetime):
        value = value.date()
    return value.strftime("%d-%m-%Y")


def stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def create_referral_code(customer_id: str, program_id: str) -> str:
    digest = hashlib.sha256(f"{program_id}:{customer_id}".encode("utf-8")).hexdigest()[:8].upper()
    safe_customer = re.sub(r"[^A-Za-z0-9]", "", customer_id)[-6:].upper()
    return f"R-{safe_customer}-{digest}"


def verify_webhook_signature(raw_body: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature.replace("sha256=", ""))


def _serialize(value: Any) -> Dict[str, Any]:
    raw = asdict(value)
    for key, item in list(raw.items()):
        if isinstance(item, Decimal):
            raw[key] = str(item)
        elif isinstance(item, Enum):
            raw[key] = item.value
    return raw


class GatewayAdapter:
    SUPPORTED = {"cardcom", "tranzila", "grow", "meshulam", "payplus", "yaadpay", "yabandpay", "manual"}

    def __init__(self, provider: str, credentials: Optional[Mapping[str, str]] = None) -> None:
        provider = provider.lower().strip()
        provider = {"meshulam": "grow", "yaadpay": "yabandpay"}.get(provider, provider)
        if provider not in self.SUPPORTED:
            raise ValidationError(f"Unsupported gateway provider: {provider}")
        self.provider = provider
        self.credentials = dict(credentials or {})

    def build_refund_request(self, transaction_id: str, amount_ils: Decimal | int | float | str, reason: str, idempotency_key: str, metadata: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        if not transaction_id:
            raise ValidationError("transaction_id is required")
        amount = money(amount_ils)
        if amount <= 0:
            raise ValidationError("amount_ils must be positive")
        return {"provider": self.provider, "operation": "refund", "transaction_id": transaction_id, "amount": str(amount), "currency": "ILS", "reason": reason, "idempotency_key": idempotency_key, "metadata": dict(metadata or {})}

    def build_credit_request(self, customer_reference: str, amount_ils: Decimal | int | float | str, expires_at: Optional[str] = None, metadata: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        amount = money(amount_ils)
        if amount <= 0:
            raise ValidationError("amount_ils must be positive")
        return {"provider": self.provider, "operation": "credit", "customer_reference": customer_reference, "amount": str(amount), "currency": "ILS", "expires_at": expires_at, "metadata": dict(metadata or {})}

    def parse_webhook(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        raw_status = str(payload.get("status") or payload.get("raw_status") or "").lower()
        reward_id = payload.get("reward_id") or (payload.get("metadata") or {}).get("reward_id") or payload.get("custom")
        if not reward_id:
            raise ValidationError("webhook payload missing reward_id")
        status_map = {"approved": "paid", "paid": "paid", "success": "paid", "refunded": "paid", "failed": "failed", "declined": "failed", "canceled": "reversed", "cancelled": "reversed"}
        return {"provider": self.provider, "event_type": str(payload.get("event_type") or payload.get("type") or "").lower(), "reward_id": reward_id, "gateway_reference": payload.get("refund_id") or payload.get("transaction_id") or payload.get("id"), "status": status_map.get(raw_status, "submitted"), "raw_status": raw_status}

    def map_error(self, code: str, message: str = "") -> Dict[str, Any]:
        code = code.upper()
        return {"provider": self.provider, "error_code": code, "message": message or code, "retryable": code in {"RATE_LIMITED", "TEMPORARY_GATEWAY_ERROR", "TIMEOUT"}}


class PaymentGatewayClient:
    def __init__(self, adapter: GatewayAdapter, sync_transport: Optional[Callable[[Mapping[str, Any]], Mapping[str, Any]]] = None, async_transport: Optional[Callable[[Mapping[str, Any]], Awaitable[Mapping[str, Any]]]] = None) -> None:
        self.adapter = adapter
        self.sync_transport = sync_transport
        self.async_transport = async_transport

    def submit(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        if self.sync_transport is None:
            return {"status": "submitted", "provider": self.adapter.provider, "gateway_reference": stable_id("gw", json.dumps(dict(payload), sort_keys=True)), "payload": dict(payload)}
        response = dict(self.sync_transport(payload))
        if response.get("status") in {"failed", "error"}:
            raise GatewayError(str(response))
        return response

    async def submit_async(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        if self.async_transport is not None:
            response = dict(await self.async_transport(payload))
            if response.get("status") in {"failed", "error"}:
                raise GatewayError(str(response))
            return response
        await asyncio.sleep(0)
        return self.submit(payload)


class ReferralProgramManager:
    def __init__(self) -> None:
        self.customers: Dict[str, Customer] = {}
        self.programs: Dict[str, ReferralProgram] = {}
        self.events: Dict[str, ReferralEvent] = {}
        self.rewards: Dict[str, Reward] = {}
        self.audit_log: list[AuditEntry] = []

    def audit(self, actor: str, action: str, entity_id: str, before: Mapping[str, Any], after: Mapping[str, Any]) -> None:
        self.audit_log.append(AuditEntry(now_iso(), actor, action, entity_id, dict(before), dict(after)))

    def add_customer(self, customer_id: str, name: str, email: str, phone: str, consent_marketing: bool = False, is_existing_customer: bool = False, is_employee: bool = False, vat_or_id: Optional[str] = None, bank_account: Optional[str] = None, metadata: Optional[Mapping[str, Any]] = None) -> Customer:
        if not customer_id:
            raise ValidationError("customer_id is required")
        before = _serialize(self.customers[customer_id]) if customer_id in self.customers else {}
        customer = Customer(customer_id, name.strip(), normalize_email(email), normalize_israeli_phone(phone), consent_marketing, is_existing_customer=is_existing_customer, is_employee=is_employee, vat_or_id=vat_or_id, bank_account=bank_account, metadata=dict(metadata or {}))
        self.customers[customer_id] = customer
        self.audit("system", "add_customer", customer_id, before, _serialize(customer))
        return customer

    def create_program(self, program_id: str, name: str, reward_type: str | RewardType, reward_amount_ils: Decimal | int | float | str, qualifying_action: str, cooldown_days: int = 14, max_rewards_per_customer: int = 5, minimum_order_ils: Decimal | int | float | str = "0.00", terms_version: str = "v1", active: bool = True, require_tax_document_for_cash: bool = True) -> ReferralProgram:
        if not program_id:
            raise ValidationError("program_id is required")
        reward_type = RewardType(reward_type)
        if money(reward_amount_ils) <= 0:
            raise ValidationError("reward_amount_ils must be positive")
        if cooldown_days < 0 or max_rewards_per_customer <= 0:
            raise ValidationError("invalid limits")
        before = _serialize(self.programs[program_id]) if program_id in self.programs else {}
        program = ReferralProgram(program_id, name, reward_type, money(reward_amount_ils), qualifying_action, cooldown_days, max_rewards_per_customer, money(minimum_order_ils), terms_version, active, require_tax_document_for_cash)
        self.programs[program_id] = program
        self.audit("system", "create_program", program_id, before, _serialize(program))
        return program

    def generate_referral_link(self, program_id: str, customer_id: str, base_url: str) -> str:
        if program_id not in self.programs or customer_id not in self.customers:
            raise ValidationError("unknown program_id or customer_id")
        sep = "&" if "?" in base_url else "?"
        return f"{base_url}{sep}ref={create_referral_code(customer_id, program_id)}&program={program_id}"

    def _find_event(self, program_id: str, referrer_id: str, referred_customer_id: str) -> Optional[ReferralEvent]:
        for event in self.events.values():
            if event.program_id == program_id and event.referrer_id == referrer_id and event.referred_customer_id == referred_customer_id:
                return event
        return None

    def score_fraud(self, referrer: Customer, referred: Customer) -> tuple[int, Optional[str]]:
        score = 0
        reasons = []
        if referrer.email == referred.email:
            score += 100; reasons.append("same_email")
        if referrer.phone == referred.phone:
            score += 100; reasons.append("same_phone")
        if referrer.vat_or_id and referrer.vat_or_id == referred.vat_or_id:
            score += 100; reasons.append("same_id")
        if referrer.metadata.get("card_token") and referrer.metadata.get("card_token") == referred.metadata.get("card_token"):
            score += 90; reasons.append("same_card_token")
        if referrer.metadata.get("ip") and referrer.metadata.get("ip") == referred.metadata.get("ip"):
            score += 20; reasons.append("same_ip")
        return min(score, 100), ",".join(reasons) if reasons else None

    def register_referral(self, program_id: str, referrer_id: str, referred_customer_id: str, source: str, allow_manual_review: bool = True) -> ReferralEvent:
        if program_id not in self.programs:
            raise ValidationError("unknown program_id")
        program = self.programs[program_id]
        if not program.active:
            raise ValidationError("program is not active")
        if referrer_id == referred_customer_id:
            raise ValidationError("self-referral is not allowed")
        if referrer_id not in self.customers or referred_customer_id not in self.customers:
            raise ValidationError("unknown customer")
        duplicate = self._find_event(program_id, referrer_id, referred_customer_id)
        if duplicate:
            raise DuplicateReferralError(f"duplicate referral: {duplicate.event_id}")
        referrer, referred = self.customers[referrer_id], self.customers[referred_customer_id]
        event = ReferralEvent(stable_id("evt", program_id, referrer_id, referred_customer_id), program_id, referrer_id, referred_customer_id, source, create_referral_code(referrer_id, program_id), terms_version=program.terms_version)
        score, reason = self.score_fraud(referrer, referred)
        event.fraud_score, event.review_reason = score, reason
        if score >= 90 or referred.is_existing_customer or referred.is_employee:
            if allow_manual_review:
                event.status = ReferralStatus.FRAUD_REVIEW
                event.review_reason = event.review_reason or "existing_customer_or_employee"
            else:
                raise ValidationError(event.review_reason or "manual review required")
        self.events[event.event_id] = event
        self.audit("system", "register_referral", event.event_id, {}, _serialize(event))
        return event

    def qualify_referral(self, event_id: str, evidence: Optional[Mapping[str, Any]] = None, order_amount_ils: Decimal | int | float | str | None = None) -> ReferralEvent:
        if event_id not in self.events:
            raise ValidationError("unknown event_id")
        event = self.events[event_id]
        program = self.programs[event.program_id]
        if event.status == ReferralStatus.FRAUD_REVIEW:
            raise ValidationError("manual review required before qualification")
        if event.status in {ReferralStatus.REJECTED, ReferralStatus.REVERSED}:
            raise ValidationError("cannot qualify rejected or reversed event")
        if order_amount_ils is not None and money(order_amount_ils) < program.minimum_order_ils:
            raise ValidationError("order amount below minimum")
        evidence = dict(evidence or {})
        if not evidence:
            raise ValidationError("qualification evidence is required")
        before = _serialize(event)
        event.status = ReferralStatus.QUALIFIED
        event.qualified_at = now_iso()
        event.evidence.update(evidence)
        self.audit("system", "qualify_referral", event_id, before, _serialize(event))
        return event

    def _approved_reward_count(self, customer_id: str, program_id: str) -> int:
        count = 0
        for reward in self.rewards.values():
            event = self.events.get(reward.event_id)
            if event and event.program_id == program_id and reward.recipient_customer_id == customer_id and reward.status in {RewardStatus.APPROVED, RewardStatus.SUBMITTED, RewardStatus.PAID}:
                count += 1
        return count

    def approve_reward(self, event_id: str, actor: str, tax_treatment: str = "unclassified", today: Optional[datetime] = None, force: bool = False) -> Reward:
        if event_id not in self.events:
            raise ValidationError("unknown event_id")
        event = self.events[event_id]
        program = self.programs[event.program_id]
        if event.status not in {ReferralStatus.QUALIFIED, ReferralStatus.REWARD_PENDING}:
            raise ValidationError(f"event must be qualified before reward approval; got {event.status}")
        if not event.qualified_at:
            raise ValidationError("qualified_at is missing")
        reference_now = today or datetime.now(timezone.utc)
        qualified_at = datetime.fromisoformat(event.qualified_at)
        if not force and reference_now < qualified_at + timedelta(days=program.cooldown_days):
            event.status = ReferralStatus.REWARD_PENDING
            raise ValidationError("cooldown period has not elapsed")
        if self._approved_reward_count(event.referrer_id, event.program_id) >= program.max_rewards_per_customer:
            event.status = ReferralStatus.FRAUD_REVIEW
            event.review_reason = "cap_reached"
            raise ValidationError("reward cap reached")
        reward_id = stable_id("rwd", event.event_id, event.referrer_id)
        if reward_id in self.rewards:
            return self.rewards[reward_id]
        reward = Reward(reward_id, event.event_id, event.referrer_id, program.reward_amount_ils, program.reward_type, RewardStatus.APPROVED, tax_treatment, idempotency_key=f"reward-{reward_id}", approved_at=now_iso())
        if reward.reward_type in {RewardType.COUPON, RewardType.CREDIT, RewardType.GIFT_CARD}:
            reward.expires_at = format_dd_mm_yyyy(datetime.now(timezone.utc).date() + timedelta(days=180))
        self.rewards[reward_id] = reward
        before = _serialize(event)
        event.status = ReferralStatus.REWARD_PENDING
        self.audit(actor, "approve_reward", reward_id, {}, _serialize(reward))
        self.audit(actor, "event_reward_pending", event.event_id, before, _serialize(event))
        return reward

    def mark_reward_paid(self, reward_id: str, gateway: Optional[str] = None, gateway_reference: Optional[str] = None, actor: str = "system") -> Reward:
        if reward_id not in self.rewards:
            raise ValidationError("unknown reward_id")
        reward = self.rewards[reward_id]
        if reward.status not in {RewardStatus.APPROVED, RewardStatus.SUBMITTED}:
            raise ValidationError(f"reward cannot be paid from status {reward.status}")
        before = _serialize(reward)
        reward.status = RewardStatus.PAID
        reward.gateway = gateway or reward.gateway
        reward.gateway_reference = gateway_reference or reward.gateway_reference
        reward.paid_at = now_iso()
        self.audit(actor, "mark_reward_paid", reward_id, before, _serialize(reward))
        return reward

    def reverse_reward(self, reward_id: str, reason: str, actor: str = "system") -> Reward:
        if reward_id not in self.rewards:
            raise ValidationError("unknown reward_id")
        reward = self.rewards[reward_id]
        before = _serialize(reward)
        reward.status = RewardStatus.REVERSED
        reward.metadata["reversal_reason"] = reason
        self.events[reward.event_id].status = ReferralStatus.REVERSED
        self.audit(actor, "reverse_reward", reward_id, before, _serialize(reward))
        return reward

    def build_reward_gateway_payload(self, reward_id: str, gateway: str, original_transaction_id: Optional[str] = None) -> Dict[str, Any]:
        if reward_id not in self.rewards:
            raise ValidationError("unknown reward_id")
        reward = self.rewards[reward_id]
        adapter = GatewayAdapter(gateway)
        if reward.reward_type == RewardType.REFUND:
            if not original_transaction_id:
                raise ValidationError("original_transaction_id is required for refund rewards")
            return adapter.build_refund_request(original_transaction_id, reward.amount_ils, "referral_reward", reward.idempotency_key or f"reward-{reward.reward_id}", {"reward_id": reward.reward_id, "event_id": reward.event_id})
        return adapter.build_credit_request(reward.recipient_customer_id, reward.amount_ils, reward.expires_at, {"reward_id": reward.reward_id, "event_id": reward.event_id})

    def apply_gateway_response(self, reward_id: str, response: Mapping[str, Any], actor: str = "gateway") -> Reward:
        if reward_id not in self.rewards:
            raise ValidationError("unknown reward_id")
        reward = self.rewards[reward_id]
        before = _serialize(reward)
        reward.gateway = str(response.get("provider") or response.get("gateway") or reward.gateway or "")
        reward.gateway_reference = str(response.get("gateway_reference") or response.get("refund_id") or response.get("credit_id") or "")
        status = str(response.get("status") or "").lower()
        if status in {"paid", "approved", "success"}:
            reward.status = RewardStatus.PAID
            reward.paid_at = now_iso()
        elif status in {"submitted", "pending"}:
            reward.status = RewardStatus.SUBMITTED
        elif status in {"reversed", "canceled", "cancelled"}:
            reward.status = RewardStatus.REVERSED
        else:
            reward.metadata["gateway_status"] = status
        self.audit(actor, "apply_gateway_response", reward_id, before, _serialize(reward))
        return reward

    def export_rewards_csv(self, path: str | Path, status: Optional[str] = None, fields: Optional[Sequence[str]] = None) -> Path:
        path = Path(path)
        fields = list(fields or ["reward_id", "event_id", "recipient_customer_id", "amount_ils", "reward_type", "status", "tax_treatment", "gateway", "gateway_reference", "document_number", "approved_at", "paid_at", "expires_at"])
        wanted = RewardStatus(status) if status else None
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for reward in self.rewards.values():
                if wanted and reward.status != wanted:
                    continue
                row = _serialize(reward)
                writer.writerow({field: row.get(field, "") for field in fields})
        return path

    def to_dict(self) -> Dict[str, Any]:
        return {"customers": {k: _serialize(v) for k, v in self.customers.items()}, "programs": {k: _serialize(v) for k, v in self.programs.items()}, "events": {k: _serialize(v) for k, v in self.events.items()}, "rewards": {k: _serialize(v) for k, v in self.rewards.items()}, "audit_log": [_serialize(v) for v in self.audit_log]}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ReferralProgramManager":
        manager = cls()
        manager.customers = {k: Customer(**v) for k, v in data.get("customers", {}).items()}
        manager.programs = {k: ReferralProgram(**{**v, "reward_type": RewardType(v["reward_type"]), "reward_amount_ils": money(v["reward_amount_ils"]), "minimum_order_ils": money(v.get("minimum_order_ils", "0.00"))}) for k, v in data.get("programs", {}).items()}
        manager.events = {k: ReferralEvent(**{**v, "status": ReferralStatus(v["status"])}) for k, v in data.get("events", {}).items()}
        manager.rewards = {k: Reward(**{**v, "reward_type": RewardType(v["reward_type"]), "status": RewardStatus(v["status"]), "amount_ils": money(v["amount_ils"])}) for k, v in data.get("rewards", {}).items()}
        manager.audit_log = [AuditEntry(**v) for v in data.get("audit_log", [])]
        return manager

    def save_json(self, path: str | Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    @classmethod
    def load_json(cls, path: str | Path) -> "ReferralProgramManager":
        path = Path(path)
        if not path.exists():
            return cls()
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))


def create_demo_manager() -> ReferralProgramManager:
    manager = ReferralProgramManager()
    manager.create_program("salon-50-2026", "Salon ₪50 Referral", RewardType.CREDIT, 50, "paid_completed_appointment", cooldown_days=0, max_rewards_per_customer=10)
    manager.add_customer("cust_1001", "Dana Levi", "dana@example.co.il", "050-1234567", True)
    manager.add_customer("cust_2002", "Noa Cohen", "noa@example.co.il", "052-7654321", True)
    event = manager.register_referral("salon-50-2026", "cust_1001", "cust_2002", "booking_form")
    manager.qualify_referral(event.event_id, {"invoice": "INV-2026-0042"}, 200)
    manager.approve_reward(event.event_id, actor="owner", tax_treatment="customer_credit")
    return manager
