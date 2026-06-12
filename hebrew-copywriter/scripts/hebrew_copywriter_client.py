"""Installable deterministic helper client for Hebrew marketing copy briefs."""

from __future__ import annotations

import asyncio
import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


VAT_RATE = Decimal("0.18")
DEFAULT_UNSUBSCRIBE = 'להסרה מהרשימה: השיבו "הסר".'


class Channel(str, Enum):
    LANDING_PAGE = "landing_page"
    INSTAGRAM = "instagram"
    WHATSAPP = "whatsapp"
    SMS = "sms"
    EMAIL = "email"
    GOOGLE_ADS = "google_ads"
    FLYER = "flyer"
    PRODUCT_PAGE = "product_page"
    QUOTE_FOLLOWUP = "quote_followup"


class Register(str, Enum):
    WARM = "warm"
    PROFESSIONAL = "professional"
    DIRECT = "direct"
    PREMIUM = "premium"
    PLAYFUL = "playful"
    FORMAL = "formal"


class GenderMode(str, Enum):
    NEUTRAL = "neutral"
    FEMININE = "feminine"
    MASCULINE = "masculine"
    MIXED = "mixed"


@dataclass(frozen=True)
class CopyBrief:
    business_name: str
    business_type: str
    offer: str
    audience: str
    channel: Channel = Channel.LANDING_PAGE
    register: Register = Register.WARM
    gender_mode: GenderMode = GenderMode.NEUTRAL
    price: Optional[Decimal] = None
    include_vat: Optional[bool] = None
    location: Optional[str] = None
    deadline: Optional[str] = None
    proof_points: List[str] = field(default_factory=list)
    compliance_notes: List[str] = field(default_factory=list)
    taboo_terms: List[str] = field(default_factory=list)
    call_to_action: Optional[str] = None
    include_unsubscribe: bool = False
    privacy_policy_url: Optional[str] = None

    def to_json(self) -> str:
        def default(value: Any) -> Any:
            if isinstance(value, Enum):
                return value.value
            if isinstance(value, Decimal):
                return str(value)
            raise TypeError(f"Unsupported type: {type(value)!r}")

        return json.dumps(asdict(self), ensure_ascii=False, default=default, indent=2)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "CopyBrief":
        payload = dict(data)
        if "channel" in payload and not isinstance(payload["channel"], Channel):
            payload["channel"] = Channel(str(payload["channel"]))
        if "register" in payload and not isinstance(payload["register"], Register):
            payload["register"] = Register(str(payload["register"]))
        if "gender_mode" in payload and not isinstance(payload["gender_mode"], GenderMode):
            payload["gender_mode"] = GenderMode(str(payload["gender_mode"]))
        if payload.get("price") not in (None, "") and not isinstance(payload["price"], Decimal):
            payload["price"] = Decimal(str(payload["price"]))
        payload.setdefault("proof_points", [])
        payload.setdefault("compliance_notes", [])
        payload.setdefault("taboo_terms", [])
        return cls(**payload)


class BriefValidationError(ValueError):
    """Raised when a brief is too incomplete to generate useful copy."""


class HebrewCopywriterClient:
    """Deterministic Hebrew copywriting helper."""

    def validate_brief(self, brief: CopyBrief) -> List[str]:
        missing = [
            name
            for name in ("business_name", "business_type", "offer", "audience")
            if not str(getattr(brief, name, "")).strip()
        ]
        if missing:
            raise BriefValidationError("Missing required fields: " + ", ".join(missing))

        warnings: List[str] = []
        if brief.price is not None and brief.include_vat is None:
            warnings.append('VAT status missing: add כולל מע"מ or לא כולל מע"מ when relevant.')
        if brief.channel in {Channel.WHATSAPP, Channel.SMS, Channel.EMAIL} and not brief.include_unsubscribe:
            warnings.append("Direct marketing copy may need unsubscribe wording under Communications Law Section 30A.")
        if brief.privacy_policy_url is None and any(term in brief.offer for term in ["טופס", "פרטים", "ליד", "הרשמה"]):
            warnings.append("Lead collection may need privacy-policy wording.")
        if brief.deadline and not self._looks_local_date(brief.deadline):
            warnings.append("Use DD/MM/YYYY date format for Israeli audience.")
        return warnings

    def generate_copy(self, brief: CopyBrief) -> Dict[str, Any]:
        warnings = self.validate_brief(brief)
        price_text = self.format_price(brief.price, brief.include_vat) if brief.price is not None else None
        cta = brief.call_to_action or self.default_cta(brief)
        proof = self._proof_sentence(brief.proof_points)
        location = f" ב{brief.location}" if brief.location else ""
        deadline = f"בתוקף עד {self.localize_date(brief.deadline)}" if brief.deadline else ""
        tone = self._tone_phrase(brief.register)
        action = self._action_phrase(brief.gender_mode)

        if brief.channel == Channel.SMS:
            text = self._sms_copy(brief, price_text, cta, deadline)
            return self._result(brief, text=text, warnings=warnings)

        if brief.channel == Channel.WHATSAPP:
            text = self._whatsapp_copy(brief, price_text, cta, proof, deadline)
            return self._result(brief, text=text, warnings=warnings)

        if brief.channel == Channel.GOOGLE_ADS:
            headlines = [
                self._trim(f"{brief.offer} ל{brief.audience}", 30),
                self._trim(f"{brief.business_type}{location}", 30),
                self._trim("בדקו התאמה לעסק", 30),
            ]
            descriptions = [
                self._trim(f"{brief.business_name}: {brief.offer}. {proof or tone}. {cta}.", 90),
                self._trim(f"פתרון ברור ל{brief.audience}, עם תהליך מסודר והנעה לפעולה מהירה.", 90),
            ]
            return self._result(brief, headlines=headlines, descriptions=descriptions, warnings=warnings)

        headline = self._headline(brief, location)
        pieces = [f"{brief.offer} ל{brief.audience}"]
        if proof:
            pieces.append(proof)
        if price_text:
            pieces.append(price_text)
        if deadline:
            pieces.append(deadline)
        subheadline = " — ".join(pieces)

        body = (
            f"{brief.business_name} מציע {brief.offer} בצורה {tone}, "
            f"עם תהליך ברור שמתאים ל{brief.audience}. "
            f"{action} לקבל מידע, להבין את האפשרויות, ולהתקדם בלי להסתבך."
        )
        if brief.privacy_policy_url:
            body += " הפרטים ישמשו ליצירת קשר בנוגע לפנייה, בהתאם למדיניות הפרטיות באתר."
        if brief.channel == Channel.PRODUCT_PAGE:
            body = f"{brief.offer} שמתאים ל{brief.audience}. {proof or 'יש להוסיף פרטי מוצר, משלוח והחזרה ליד המחיר.'}"
        if brief.channel == Channel.QUOTE_FOLLOWUP:
            body = (
                f"בהמשך לשיחה, מצורפת הצעה עבור {brief.offer}. "
                f"העבודה מתאימה ל{brief.audience}, כוללת תהליך מסודר ותוצרים ברורים. "
                f"{price_text or 'את המחיר יש לציין לצד היקף העבודה.'}"
            )

        return self._result(
            brief,
            headline=headline,
            subheadline=subheadline,
            body=body,
            cta=cta,
            warnings=warnings,
        )

    def build_prompt(self, brief: CopyBrief) -> str:
        warnings = self.validate_brief(brief)
        payload = json.loads(brief.to_json())
        return (
            "כתוב קופי שיווקי בעברית ישראלית טבעית לפי הבריף הבא.\n"
            "הקפד על משלב מתאים, לשון מגדרית עקבית, ₪, תאריכים בפורמט DD/MM/YYYY, "
            "מע\"מ, פרטיות, הסרה מדיוור וטענות זהירות בתחומים רגישים.\n\n"
            f"בריף:\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n\n"
            f"אזהרות לבדיקה:\n{json.dumps(warnings, ensure_ascii=False, indent=2)}"
        )

    def compliance_check(self, text: str, channel: Channel = Channel.LANDING_PAGE) -> List[str]:
        issues: List[str] = []
        for pattern, message in [
            (r"100%|מובטח|בוודאות", "Unsupported guarantee: soften or add proof and conditions."),
            (r"הכי זול|מספר 1|הטוב ביותר", "Unverified superiority claim."),
            (r"מרפא|מרפאה|ריפוי", "Medical claim: verify legal/professional basis."),
            (r"תשואה מובטחת|רווח מובטח", "Financial guarantee risk."),
            (r"חיסכון במס מובטח", "Tax guarantee risk."),
        ]:
            if re.search(pattern, text):
                issues.append(message)
        if channel in {Channel.SMS, Channel.WHATSAPP, Channel.EMAIL} and "הסר" not in text and "להסרה" not in text:
            issues.append("Direct marketing message lacks unsubscribe wording.")
        if "₪" in text and "מע\"מ" not in text and "מע״מ" not in text:
            issues.append("Price appears without VAT clarification; verify whether this is acceptable for the audience.")
        if re.search(r"\d{4}[-/]\d{2}[-/]\d{2}", text) or re.search(r"\d{2}-\d{2}-\d{4}", text):
            issues.append("Date appears in non-local format; use DD/MM/YYYY for Israeli-facing copy.")
        return issues

    def generate_variants(self, brief: CopyBrief, count: int = 3) -> List[Dict[str, Any]]:
        registers = [brief.register, Register.DIRECT, Register.PROFESSIONAL, Register.PREMIUM, Register.PLAYFUL]
        variants: List[Dict[str, Any]] = []
        seen: set[str] = set()
        for register in registers:
            if register.value in seen:
                continue
            seen.add(register.value)
            varied = CopyBrief.from_mapping({**json.loads(brief.to_json()), "register": register.value})
            generated = self.generate_copy(varied)
            generated["variant_register"] = register.value
            variants.append(generated)
            if len(variants) >= count:
                break
        return variants

    def format_price(self, price: Optional[Decimal], include_vat: Optional[bool] = None) -> str:
        if price is None:
            return ""
        amount = Decimal(price)
        text = f"₪{int(amount):,}" if amount == amount.to_integral() else f"₪{amount:,.2f}"
        if include_vat is True:
            return f'{text} כולל מע"מ'
        if include_vat is False:
            return f'{text} לא כולל מע"מ'
        return text

    def price_with_vat(self, net_price: Decimal, rate: Decimal = VAT_RATE) -> Decimal:
        return (Decimal(net_price) * (Decimal("1") + rate)).quantize(Decimal("0.01"))

    def localize_date(self, value: Optional[str]) -> str:
        if not value:
            return ""
        raw = str(value).strip()
        if self._looks_local_date(raw):
            return raw
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(raw, fmt).strftime("%d/%m/%Y")
            except ValueError:
                continue
        return raw

    def default_cta(self, brief: CopyBrief) -> str:
        if brief.channel == Channel.PRODUCT_PAGE:
            return "להוספה לעגלה"
        if brief.channel == Channel.QUOTE_FOLLOWUP:
            return "לאישור ההצעה"
        if brief.channel == Channel.GOOGLE_ADS:
            return "בדקו התאמה"
        if brief.gender_mode == GenderMode.FEMININE:
            return "קבלי פרטים"
        if brief.gender_mode == GenderMode.MASCULINE:
            return "קבל פרטים"
        if brief.gender_mode == GenderMode.MIXED:
            return "בואו לבדוק התאמה"
        return "לקבלת פרטים"

    def _result(self, brief: CopyBrief, warnings: Sequence[str], **payload: Any) -> Dict[str, Any]:
        text_for_checks = "\n".join(str(v) for v in payload.values() if isinstance(v, str))
        return {
            "business_name": brief.business_name,
            "channel": brief.channel.value,
            "register": brief.register.value,
            "gender_mode": brief.gender_mode.value,
            **payload,
            "warnings": list(warnings),
            "compliance_issues": self.compliance_check(text_for_checks, brief.channel),
        }

    def _headline(self, brief: CopyBrief, location: str) -> str:
        if brief.register == Register.PREMIUM:
            return f"{brief.offer} עם גימור מוקפד{location}"
        if brief.register == Register.PLAYFUL:
            return f"{brief.offer} שסוגר פינה ל{brief.audience}"
        if brief.register == Register.FORMAL:
            return f"שירות {brief.business_type} עבור {brief.audience}{location}"
        return f"{brief.offer} ל{brief.audience}{location}"

    def _proof_sentence(self, proof_points: Iterable[str]) -> str:
        points = [p.strip() for p in proof_points if p and p.strip()]
        if not points:
            return ""
        if len(points) == 1:
            return points[0]
        return "כולל " + ", ".join(points[:-1]) + f" ו{points[-1]}"

    def _tone_phrase(self, register: Register) -> str:
        return {
            Register.WARM: "נעימה וברורה",
            Register.PROFESSIONAL: "מקצועית ומסודרת",
            Register.DIRECT: "ישירה ותכליתית",
            Register.PREMIUM: "מוקפדת ושקטה",
            Register.PLAYFUL: "קלילה וישראלית",
            Register.FORMAL: "רשמית ומכבדת",
        }[register]

    def _action_phrase(self, gender: GenderMode) -> str:
        return {
            GenderMode.FEMININE: "קבלי דרך פשוטה",
            GenderMode.MASCULINE: "קבל דרך פשוטה",
            GenderMode.MIXED: "בואו לקבל דרך פשוטה",
            GenderMode.NEUTRAL: "אפשר",
        }[gender]

    def _sms_copy(self, brief: CopyBrief, price_text: Optional[str], cta: str, deadline: str) -> str:
        parts = [f"{brief.business_name}: {brief.offer} ל{brief.audience}"]
        if price_text:
            parts.append(price_text)
        if deadline:
            parts.append(deadline)
        parts.append(cta)
        text = ". ".join(parts)
        if brief.include_unsubscribe:
            text += ". להסרה: השיבו הסר"
        return self._trim(text, 160)

    def _whatsapp_copy(self, brief: CopyBrief, price_text: Optional[str], cta: str, proof: str, deadline: str) -> str:
        lines = [f"היי, כאן {brief.business_name}.", f"נפתחה אפשרות ל{brief.offer} עבור {brief.audience}."]
        if proof:
            lines.append(proof + ".")
        if price_text:
            lines.append(f"עלות: {price_text}.")
        if deadline:
            lines.append(deadline + ".")
        lines.append(f"{cta}: [קישור]")
        if brief.include_unsubscribe:
            lines.append(DEFAULT_UNSUBSCRIBE)
        return "\n".join(lines)

    def _trim(self, text: str, limit: int) -> str:
        cleaned = re.sub(r"\s+", " ", text).strip()
        return cleaned if len(cleaned) <= limit else cleaned[: max(0, limit - 1)].rstrip() + "…"

    def _looks_local_date(self, value: str) -> bool:
        return bool(re.fullmatch(r"\d{2}/\d{2}/\d{4}", str(value).strip()))


class AsyncHebrewCopywriterClient:
    def __init__(self, client: Optional[HebrewCopywriterClient] = None) -> None:
        self._client = client or HebrewCopywriterClient()

    async def generate_copy(self, brief: CopyBrief) -> Dict[str, Any]:
        return await asyncio.to_thread(self._client.generate_copy, brief)

    async def build_prompt(self, brief: CopyBrief) -> str:
        return await asyncio.to_thread(self._client.build_prompt, brief)

    async def compliance_check(self, text: str, channel: Channel = Channel.LANDING_PAGE) -> List[str]:
        return await asyncio.to_thread(self._client.compliance_check, text, channel)


def brief_template() -> Dict[str, Any]:
    return {
        "business_name": "סטודיו נועה",
        "business_type": "פילאטיס",
        "offer": "קבוצת בוקר קטנה",
        "audience": "נשים אחרי לידה",
        "channel": "instagram",
        "register": "warm",
        "gender_mode": "feminine",
        "price": "220",
        "include_vat": True,
        "location": "רמת גן",
        "deadline": "30/06/2026",
        "proof_points": ["עד 8 משתתפות", "מדריכה מוסמכת", "התאמה אישית"],
        "compliance_notes": [],
        "taboo_terms": ["חזרה לגזרה"],
        "call_to_action": "שלחו הודעה בפרטי",
        "include_unsubscribe": False,
        "privacy_policy_url": None,
    }


def brief_from_json_file(path: str) -> CopyBrief:
    with open(path, "r", encoding="utf-8") as handle:
        return CopyBrief.from_mapping(json.load(handle))


def save_brief(brief: CopyBrief, store_dir: Optional[str] = None) -> Dict[str, str]:
    directory = Path(store_dir or ".hebrew-copywriter/briefs")
    directory.mkdir(parents=True, exist_ok=True)
    brief_id = uuid.uuid4().hex[:12]
    path = directory / f"{brief_id}.json"
    path.write_text(brief.to_json(), encoding="utf-8")
    return {"id": brief_id, "path": str(path)}


def load_saved_brief(brief_id: str, store_dir: Optional[str] = None) -> CopyBrief:
    directory = Path(store_dir or ".hebrew-copywriter/briefs")
    path = directory / f"{brief_id}.json"
    return brief_from_json_file(str(path))


__all__ = [
    "AsyncHebrewCopywriterClient",
    "BriefValidationError",
    "Channel",
    "CopyBrief",
    "GenderMode",
    "HebrewCopywriterClient",
    "Register",
    "VAT_RATE",
    "brief_from_json_file",
    "brief_template",
    "load_saved_brief",
    "save_brief",
]
