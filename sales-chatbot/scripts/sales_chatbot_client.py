#!/usr/bin/env python3
"""Typed Hebrew sales chatbot helper for Israeli businesses.

Run this module inside a CRM job, WhatsApp webhook, storefront backend, or local CLI without external services.
"""

from __future__ import annotations

import asyncio
import datetime as _dt
import hashlib
import json
import math
import os
import re
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


ILS = "₪"
DEFAULT_VAT_RATE = Decimal("0.18")
HEBREW_YES = {"כן", "יאללה", "סבבה", "מעוניין", "מעוניינת", "רוצה", "אשמח", "קונה"}
HEBREW_NO = {"לא", "עזבו", "בטל", "ביטול", "הסר", "הסרה", "להסיר", "תפסיק", "להפסיק", "די"}
COMPLAINT_TERMS = {"בעיה", "תקלה", "לא עובד", "שבור", "כועס", "כועסת", "תלונה", "מאוכזב", "מאוכזבת"}
PRICE_TERMS = {"מחיר", "כמה עולה", "עלות", "₪", "שקל", "שקלים", "תשלומים", "מבצע"}
SHIPPING_TERMS = {"משלוח", "אספקה", "הגעה", "שליח", "איסוף", "נקודת איסוף"}
WARRANTY_TERMS = {"אחריות", "החלפה", "החזרה", "ביטול עסקה", "זיכוי"}
BUY_TERMS = {"לקנות", "להזמין", "הזמנה", "לתשלום", "קופה", "סליקה", "קונה", "אקח"}
COMPARE_TERMS = {"להשוות", "השוואה", "הבדל", "מול", "עדיף", "איזה כדאי"}


@dataclass(frozen=True)
class Product:
    """Catalog item used by the recommendation engine."""

    sku: str
    name_he: str
    category: str
    price_ils: Decimal
    tags: Tuple[str, ...] = field(default_factory=tuple)
    cross_sell: Tuple[str, ...] = field(default_factory=tuple)
    upsell_to: Optional[str] = None
    stock: int = 999
    max_installments: int = 1
    warranty_months: Optional[int] = None
    requires_age_confirmation: bool = False

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "Product":
        required = {"sku", "name_he", "category", "price_ils"}
        missing = sorted(required - set(raw))
        if missing:
            raise ValueError(f"Missing required product fields: {', '.join(missing)}")
        return cls(
            sku=str(raw["sku"]),
            name_he=str(raw["name_he"]),
            category=str(raw["category"]),
            price_ils=Decimal(str(raw["price_ils"])),
            tags=tuple(str(x) for x in raw.get("tags", ())),
            cross_sell=tuple(str(x) for x in raw.get("cross_sell", ())),
            upsell_to=str(raw["upsell_to"]) if raw.get("upsell_to") else None,
            stock=int(raw.get("stock", 999)),
            max_installments=max(1, int(raw.get("max_installments", 1))),
            warranty_months=int(raw["warranty_months"]) if raw.get("warranty_months") is not None else None,
            requires_age_confirmation=bool(raw.get("requires_age_confirmation", False)),
        )


@dataclass(frozen=True)
class CustomerContext:
    """Conversation state known at decision time."""

    name: Optional[str] = None
    city: Optional[str] = None
    segment: str = "consumer"
    has_marketing_consent: bool = False
    preferred_installments: Optional[int] = None
    budget_ils: Optional[Decimal] = None
    cart_skus: Tuple[str, ...] = field(default_factory=tuple)
    channel: str = "whatsapp"
    conversation_date: _dt.date = field(default_factory=_dt.date.today)

    @classmethod
    def from_mapping(cls, raw: Optional[Mapping[str, Any]]) -> "CustomerContext":
        if not raw:
            return cls()
        return cls(
            name=str(raw["name"]) if raw.get("name") else None,
            city=str(raw["city"]) if raw.get("city") else None,
            segment=str(raw.get("segment", "consumer")),
            has_marketing_consent=bool(raw.get("has_marketing_consent", False)),
            preferred_installments=int(raw["preferred_installments"]) if raw.get("preferred_installments") else None,
            budget_ils=Decimal(str(raw["budget_ils"])) if raw.get("budget_ils") is not None else None,
            cart_skus=tuple(str(x) for x in raw.get("cart_skus", ())),
            channel=str(raw.get("channel", "whatsapp")),
            conversation_date=_parse_date(raw.get("conversation_date")) if raw.get("conversation_date") else _dt.date.today(),
        )


@dataclass(frozen=True)
class OfferLine:
    sku: str
    title: str
    price: Decimal
    reason: str
    relation: str
    available: bool
    installment_line: Optional[str] = None


@dataclass(frozen=True)
class ChatbotResponse:
    intent: str
    reply_he: str
    offers: Tuple[OfferLine, ...] = field(default_factory=tuple)
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    handoff_required: bool = False
    compliance_notes: Tuple[str, ...] = field(default_factory=tuple)
    quote_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "reply_he": self.reply_he,
            "offers": [offer_line_to_dict(line) for line in self.offers],
            "warnings": list(self.warnings),
            "handoff_required": self.handoff_required,
            "compliance_notes": list(self.compliance_notes),
            "quote_id": self.quote_id,
        }


@dataclass(frozen=True)
class ChatbotConfig:
    business_name: str = "העסק"
    vat_rate: Decimal = DEFAULT_VAT_RATE
    default_installments: int = 3
    max_cross_sell_items: int = 2
    handoff_phone: str = "03-0000000"
    allow_marketing_without_consent: bool = False
    shipping_terms_he: str = "משלוח עד 3 ימי עסקים ברוב אזורי הארץ, בכפוף לזמינות."
    return_terms_he: str = "ניתן לבקש ביטול או החזרה לפי תנאי העסק והדין החל בישראל."
    quote_valid_days: int = 7


class SalesChatbotClient:
    """Rule-based recommendation client with sync and async methods."""

    def __init__(
        self,
        catalog: Sequence[Product] | Sequence[Mapping[str, Any]],
        config: Optional[ChatbotConfig] = None,
    ) -> None:
        self.config = config or ChatbotConfig()
        products: List[Product] = []
        for item in catalog:
            products.append(item if isinstance(item, Product) else Product.from_mapping(item))
        if not products:
            raise ValueError("Catalog must contain at least one product.")
        skus = [p.sku for p in products]
        duplicates = sorted({sku for sku in skus if skus.count(sku) > 1})
        if duplicates:
            raise ValueError(f"Duplicate product SKUs: {', '.join(duplicates)}")
        self.catalog: Dict[str, Product] = {p.sku: p for p in products}
        self._search_index = self._build_search_index(products)

    @classmethod
    def from_json(cls, path: str | Path, config: Optional[ChatbotConfig] = None) -> "SalesChatbotClient":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(data, Mapping):
            items = data.get("products", [])
            cfg_raw = data.get("config", {})
            merged = config or ChatbotConfig(**{k: v for k, v in cfg_raw.items() if k in ChatbotConfig.__dataclass_fields__})
            return cls(items, merged)
        return cls(data, config)

    def validate_catalog(self) -> List[str]:
        errors: List[str] = []
        for product in self.catalog.values():
            if product.price_ils <= 0:
                errors.append(f"{product.sku}: price_ils must be positive")
            if product.upsell_to and product.upsell_to not in self.catalog:
                errors.append(f"{product.sku}: upsell_to references missing SKU {product.upsell_to}")
            for sku in product.cross_sell:
                if sku not in self.catalog:
                    errors.append(f"{product.sku}: cross_sell references missing SKU {sku}")
            if product.max_installments < 1:
                errors.append(f"{product.sku}: max_installments must be at least 1")
        return errors

    def classify_intent(self, message: str) -> str:
        normalized = _normalize(message)
        if any(term in normalized for term in HEBREW_NO):
            if "הסר" in normalized or "הסרה" in normalized or "להסיר" in normalized or "תפסיק" in normalized:
                return "unsubscribe"
        if any(term in normalized for term in COMPLAINT_TERMS):
            return "complaint"
        if any(term in normalized for term in BUY_TERMS):
            return "buy"
        if any(term in normalized for term in COMPARE_TERMS):
            return "compare"
        if any(term in normalized for term in PRICE_TERMS):
            return "price"
        if any(term in normalized for term in SHIPPING_TERMS):
            return "shipping"
        if any(term in normalized for term in WARRANTY_TERMS):
            return "warranty"
        if any(term in normalized for term in {"שלום", "היי", "אהלן", "בוקר טוב", "ערב טוב"}):
            return "greeting"
        return "general"

    def recommend(self, message: str, context: Optional[CustomerContext | Mapping[str, Any]] = None) -> ChatbotResponse:
        ctx = context if isinstance(context, CustomerContext) else CustomerContext.from_mapping(context)
        intent = self.classify_intent(message)
        warnings: List[str] = []
        compliance_notes: List[str] = []
        handoff = intent in {"complaint"}

        if intent == "unsubscribe":
            return ChatbotResponse(
                intent=intent,
                reply_he="בוצע. יש להסיר את הלקוח מרשימת דיוור והודעות שיווקיות, ולשלוח רק הודעות שירות הכרחיות.",
                warnings=("בקשת הסרה משיווק זוהתה.",),
                handoff_required=True,
                compliance_notes=("חוק התקשורת סעיף 30א: כבד בקשות הסרה ללא דיחוי.",),
                quote_id=self._quote_id(message, ctx),
            )

        if not ctx.has_marketing_consent and not self.config.allow_marketing_without_consent:
            compliance_notes.append("אין לשלוח מסר שיווקי יזום ללא הסכמה מפורשת; מענה לפנייה פעילה מותר בזהירות ובהקשר הפנייה.")

        target = self._find_best_product(message, ctx)
        if target is None:
            reply = self._fallback_reply(intent, ctx)
            return ChatbotResponse(
                intent=intent,
                reply_he=reply,
                warnings=tuple(warnings),
                handoff_required=handoff,
                compliance_notes=tuple(compliance_notes),
                quote_id=self._quote_id(message, ctx),
            )

        offers = self._build_offers(target, ctx)
        if target.stock <= 0:
            warnings.append(f"{target.name_he} אינו זמין כרגע במלאי.")
            handoff = True
        if target.requires_age_confirmation:
            warnings.append("יש לוודא גיל וזכאות לפני השלמת עסקה.")
            compliance_notes.append("מוצר עם מגבלת גיל או זכאות דורש אימות לפני רכישה.")

        reply = self._compose_reply(intent, target, offers, ctx)
        return ChatbotResponse(
            intent=intent,
            reply_he=reply,
            offers=tuple(offers),
            warnings=tuple(warnings),
            handoff_required=handoff,
            compliance_notes=tuple(compliance_notes),
            quote_id=self._quote_id(message, ctx, target.sku),
        )

    async def recommend_async(
        self,
        message: str,
        context: Optional[CustomerContext | Mapping[str, Any]] = None,
    ) -> ChatbotResponse:
        await asyncio.sleep(0)
        return self.recommend(message, context)

    def make_quote(self, response: ChatbotResponse) -> str:
        lines = [
            f"הצעת מחיר {response.quote_id}",
            f"תאריך: {format_date_he(_dt.date.today())}",
            "",
            response.reply_he,
        ]
        if response.offers:
            lines.append("")
            lines.append("פריטים:")
            for offer in response.offers:
                availability = "זמין" if offer.available else "לא זמין"
                installment = f" — {offer.installment_line}" if offer.installment_line else ""
                lines.append(f"- {offer.title}: {format_ils(offer.price)} ({availability}){installment}")
        if response.compliance_notes:
            lines.append("")
            lines.append("הערות תפעול:")
            lines.extend(f"- {note}" for note in response.compliance_notes)
        return "\n".join(lines)

    def _build_search_index(self, products: Sequence[Product]) -> Dict[str, List[str]]:
        index: Dict[str, List[str]] = {}
        for p in products:
            tokens = set(_tokenize(p.name_he)) | set(_tokenize(p.category)) | set(p.tags) | {p.sku.lower()}
            for token in tokens:
                index.setdefault(token, []).append(p.sku)
        return index

    def _find_best_product(self, message: str, ctx: CustomerContext) -> Optional[Product]:
        tokens = _tokenize(message)
        scores: Dict[str, int] = {}
        for token in tokens:
            for sku in self._search_index.get(token, []):
                scores[sku] = scores.get(sku, 0) + 2
        for sku in ctx.cart_skus:
            if sku in self.catalog:
                scores[sku] = scores.get(sku, 0) + 4
        if not scores:
            available = [p for p in self.catalog.values() if p.stock > 0]
            return min(available or list(self.catalog.values()), key=lambda p: p.price_ils)
        best_sku = sorted(scores.items(), key=lambda item: (-item[1], self.catalog[item[0]].price_ils))[0][0]
        return self.catalog[best_sku]

    def _build_offers(self, target: Product, ctx: CustomerContext) -> List[OfferLine]:
        offers: List[OfferLine] = [self._line(target, "מוצר מבוקש", "base", ctx)]
        upsell = self._select_upsell(target, ctx)
        if upsell:
            offers.append(self._line(upsell, "שדרוג משתלם ביחס לצורך שתואר", "upsell", ctx))
        added = 0
        for sku in target.cross_sell:
            if sku in self.catalog and added < self.config.max_cross_sell_items:
                product = self.catalog[sku]
                if product.sku != target.sku:
                    offers.append(self._line(product, "משלים את המוצר הראשי ומעלה ערך לעסקה", "cross_sell", ctx))
                    added += 1
        return offers

    def _select_upsell(self, target: Product, ctx: CustomerContext) -> Optional[Product]:
        if not target.upsell_to or target.upsell_to not in self.catalog:
            return None
        upsell = self.catalog[target.upsell_to]
        if upsell.price_ils <= target.price_ils:
            return None
        if ctx.budget_ils is not None and upsell.price_ils > ctx.budget_ils:
            return None
        if upsell.stock <= 0:
            return None
        return upsell

    def _line(self, product: Product, reason: str, relation: str, ctx: CustomerContext) -> OfferLine:
        installments = ctx.preferred_installments or min(product.max_installments, self.config.default_installments)
        installment_line = installment_text(product.price_ils, installments, product.max_installments)
        return OfferLine(
            sku=product.sku,
            title=product.name_he,
            price=product.price_ils,
            reason=reason,
            relation=relation,
            available=product.stock > 0,
            installment_line=installment_line,
        )

    def _compose_reply(
        self,
        intent: str,
        target: Product,
        offers: Sequence[OfferLine],
        ctx: CustomerContext,
    ) -> str:
        greeting = f"{ctx.name}, " if ctx.name else ""
        valid_until = ctx.conversation_date + _dt.timedelta(days=self.config.quote_valid_days)
        lines: List[str] = []
        if intent == "shipping":
            lines.append(f"{greeting}{self.config.shipping_terms_he}")
        elif intent == "warranty":
            warranty = f"אחריות {target.warranty_months} חודשים" if target.warranty_months else "אחריות לפי תנאי היצרן והעסק"
            lines.append(f"{greeting}{warranty}. {self.config.return_terms_he}")
        elif intent == "compare":
            lines.append(f"{greeting}לפי מה שתואר, כדאי להתחיל מ־{target.name_he} ולבדוק שדרוג רק אם הערך העסקי מצדיק את ההפרש.")
        elif intent == "buy":
            lines.append(f"{greeting}אפשר להתקדם להזמנה. לפני תשלום יש לאשר מלאי, מחיר סופי, משלוח ופרטי חשבונית.")
        else:
            lines.append(f"{greeting}האפשרות המתאימה ביותר היא {target.name_he} במחיר {format_ils(target.price_ils)}, בכפוף לאישור סופי בקופה.")

        for offer in offers:
            prefix = {"base": "עיקרי", "upsell": "שדרוג", "cross_sell": "תוספת"}.get(offer.relation, "הצעה")
            installment = f" ({offer.installment_line})" if offer.installment_line else ""
            lines.append(f"{prefix}: {offer.title} — {format_ils(offer.price)}{installment}. {offer.reason}.")

        lines.append(f"תוקף הצעה: עד {format_date_he(valid_until)}.")
        lines.append("אין לשמור פרטי אשראי בצ׳אט. מעבר לתשלום יתבצע בקישור מאובטח בלבד.")
        return "\n".join(lines)

    def _fallback_reply(self, intent: str, ctx: CustomerContext) -> str:
        if intent == "complaint":
            return f"תודה על העדכון. יש להעביר לנציג שירות בטלפון {self.config.handoff_phone} עם תיאור התקלה ומספר הזמנה אם קיים."
        if intent == "greeting":
            return "שלום, אפשר לעזור בבחירת מוצר, מחיר, משלוח, אחריות או התאמה לעסק."
        return "כדי להציע מוצר מדויק, יש לציין צורך, תקציב, כמות רצויה, עיר למשלוח והעדפת תשלומים."

    def _quote_id(self, message: str, ctx: CustomerContext, sku: str = "") -> str:
        raw = "|".join([message, ctx.name or "", ctx.city or "", sku, str(ctx.conversation_date)])
        digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:8].upper()
        return f"SC-{ctx.conversation_date.strftime('%d%m%Y')}-{digest}"


def offer_line_to_dict(line: OfferLine) -> Dict[str, Any]:
    """Return an API-safe dictionary for one offer line."""
    return {
        "sku": line.sku,
        "title": line.title,
        "price": str(line.price),
        "reason": line.reason,
        "relation": line.relation,
        "available": line.available,
        "installment_line": line.installment_line,
    }


def format_ils(amount: Decimal | int | float | str, include_vat: bool = True) -> str:
    value = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    formatted = f"{value:,.2f}"
    suffix = " כולל מע״מ" if include_vat else ""
    return f"{ILS}{formatted}{suffix}"


def installment_text(total: Decimal | int | float | str, requested: Optional[int], max_installments: int) -> Optional[str]:
    if not requested or requested <= 1 or max_installments <= 1:
        return None
    count = min(int(requested), int(max_installments))
    amount = (Decimal(str(total)) / Decimal(count)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return f"עד {count} תשלומים שווים של {format_ils(amount)}; סך הכול {format_ils(total)}"


def format_date_he(date_value: _dt.date) -> str:
    return date_value.strftime("%d/%m/%Y")


def load_catalog(path: str | Path) -> List[Product]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    raw_products = data.get("products", data) if isinstance(data, Mapping) else data
    return [Product.from_mapping(item) for item in raw_products]


def validate_catalog_data(raw_products: Sequence[Mapping[str, Any]]) -> List[str]:
    errors: List[str] = []
    seen: set[str] = set()
    parsed: List[Product] = []
    for idx, raw in enumerate(raw_products):
        try:
            product = Product.from_mapping(raw)
        except Exception as exc:  # noqa: BLE001 - convert validation exceptions to user-facing errors
            errors.append(f"item {idx}: {exc}")
            continue
        if product.sku in seen:
            errors.append(f"{product.sku}: duplicate SKU")
        seen.add(product.sku)
        parsed.append(product)
    if parsed:
        sku_counts: Dict[str, int] = {}
        for product in parsed:
            sku_counts[product.sku] = sku_counts.get(product.sku, 0) + 1
        if any(count > 1 for count in sku_counts.values()):
            return errors
        client = SalesChatbotClient(parsed)
        errors.extend(client.validate_catalog())
    return errors


def load_environment_defaults(env: str = "sandbox") -> Dict[str, str]:
    """Read optional environment settings used by examples and CLIs."""
    normalized = env.lower().strip()
    if normalized not in {"sandbox", "production"}:
        raise ValueError("env must be sandbox or production")
    return {
        "env": normalized,
        "api_key_present": "true" if os.environ.get("SALES_CHATBOT_API_KEY") else "false",
        "catalog_path": os.environ.get("SALES_CHATBOT_CATALOG", ""),
        "context_path": os.environ.get("SALES_CHATBOT_CONTEXT", ""),
        "default_channel": os.environ.get("SALES_CHATBOT_CHANNEL", "whatsapp"),
    }


def sample_catalog() -> List[Dict[str, Any]]:
    return [
        {
            "sku": "BASIC-CRM",
            "name_he": "חבילת CRM בסיסית",
            "category": "תוכנה לעסקים קטנים",
            "price_ils": "249",
            "tags": ["crm", "לקוחות", "עסק", "ניהול", "לידים"],
            "cross_sell": ["SETUP-1H", "WA-TEMPLATES"],
            "upsell_to": "PRO-CRM",
            "stock": 999,
            "max_installments": 3,
            "warranty_months": 12,
        },
        {
            "sku": "PRO-CRM",
            "name_he": "חבילת CRM מקצועית",
            "category": "תוכנה לעסקים קטנים",
            "price_ils": "499",
            "tags": ["crm", "אוטומציה", "עסק", "לידים", "דוחות"],
            "cross_sell": ["SETUP-1H", "WA-TEMPLATES"],
            "stock": 999,
            "max_installments": 6,
            "warranty_months": 12,
        },
        {
            "sku": "SETUP-1H",
            "name_he": "שעת הקמה והדרכה",
            "category": "שירות",
            "price_ils": "180",
            "tags": ["הדרכה", "הטמעה", "הקמה", "שירות"],
            "stock": 999,
            "max_installments": 1,
        },
        {
            "sku": "WA-TEMPLATES",
            "name_he": "סט תבניות וואטסאפ מכירתיות",
            "category": "שיווק",
            "price_ils": "120",
            "tags": ["וואטסאפ", "תבניות", "שיווק", "מכירות"],
            "stock": 999,
            "max_installments": 2,
        },
    ]


def _normalize(message: str) -> str:
    return re.sub(r"\s+", " ", message.strip().lower())


def _tokenize(message: str) -> List[str]:
    cleaned = re.sub(r"[^\w\u0590-\u05FF]+", " ", _normalize(message))
    return [token for token in cleaned.split() if token]


def _parse_date(value: Any) -> _dt.date:
    if isinstance(value, _dt.date):
        return value
    text = str(value)
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return _dt.datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError("conversation_date must use DD/MM/YYYY, DD-MM-YYYY, or YYYY-MM-DD")


__all__ = [
    "ChatbotConfig",
    "ChatbotResponse",
    "CustomerContext",
    "OfferLine",
    "Product",
    "SalesChatbotClient",
    "format_date_he",
    "format_ils",
    "installment_text",
    "load_catalog",
    "load_environment_defaults",
    "offer_line_to_dict",
    "sample_catalog",
    "validate_catalog_data",
]


def _demo() -> None:
    client = SalesChatbotClient(sample_catalog())
    context = CustomerContext(name="דנה", has_marketing_consent=True, preferred_installments=3, budget_ils=Decimal("600"))
    print(client.recommend("כמה עולה CRM לעסק קטן?", context).reply_he)


if __name__ == "__main__":
    _demo()
