"""Typed lead routing client for Israeli lead intake workflows."""
from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union

SUPPORTED_LANGUAGES = {"HE", "EN", "RU", "AR"}
PRIORITY_ORDER = {"low": 0, "normal": 1, "high": 2, "urgent": 3}

LANGUAGE_ALIASES = {
    "he": "HE", "heb": "HE", "hebrew": "HE", "עברית": "HE", "iw": "HE",
    "en": "EN", "eng": "EN", "english": "EN", "אנגלית": "EN",
    "ru": "RU", "rus": "RU", "russian": "RU", "русский": "RU", "רוסית": "RU",
    "ar": "AR", "ara": "AR", "arabic": "AR", "العربية": "AR", "ערבית": "AR",
}

REGION_ALIASES = {
    "CENTER": ["center","central","merkaz","מרכז","גוש דן","תל אביב","tel aviv","רמת גן","גבעתיים","חולון","בת ים","פתח תקווה","פתח-תקווה","בני ברק","ראשון לציון","רחובות","נס ציונה","מודיעין","לוד","רמלה","קרית אונו","קריית אונו","ramat gan","givatayim","holon","bat yam","petah tikva","rishon lezion","rehovot","modiin","lod","ramla"],
    "SHARON": ["sharon","שרון","נתניה","הרצליה","רעננה","כפר סבא","חדרה","עמק חפר","רמת השרון","הוד השרון","netanya","herzliya","raanana","ra'anana","kfar saba","hadera","hod hasharon","ramat hasharon"],
    "HAIFA": ["haifa","חיפה","קריות","הקריות","קריית אתא","קרית אתא","קריית ביאליק","קרית ביאליק","קריית מוצקין","קרית מוצקין","קריית ים","קרית ים","נשר","טירת כרמל","nesher","tirat carmel","krayot"],
    "NORTH": ["north","צפון","גליל","גולן","נצרת","עפולה","טבריה","כרמיאל","צפת","נהריה","עכו","מגדל העמק","סכנין","שפרעם","טמרה","אום אל-פחם","nazareth","afula","tiberias","karmiel","safed","nahariya","acre","umm al-fahm","الناصرة","سخنين","طمرة","شفا عمرو"],
    "JERUSALEM": ["jerusalem","ירושלים","בית שמש","מעלה אדומים","מבשרת ציון","beit shemesh","maale adumim","mevaseret"],
    "SOUTH": ["south","דרום","נגב","באר שבע","באר-שבע","אשדוד","אשקלון","קריית גת","קרית גת","דימונה","ערד","נתיבות","אופקים","שדרות","רהט","beer sheva","beersheba","ashdod","ashkelon","kiryat gat","dimona","arad","netivot","ofakim","sderot","rahat"],
    "EILAT": ["eilat","אילת","ערבה","arava","יטבתה","yotvata"],
    "WEST_BANK": ["west bank","judea","samaria","יהודה ושומרון","יו\"ש","אריאל","מודיעין עילית","ביתר עילית","אפרת","ariel","modiin illit","beitar illit","efrat"],
}

PRODUCT_ALIASES = {
    "billing": ["billing","invoice","receipt","payment","refund","charge","חשבונית","חשבונית מס","קבלה","חיוב","תשלום","החזר","זיכוי","счет","оплата","квитанция","فاتورة","دفع","إيصال"],
    "support": ["support","problem","broken","not working","does not work","help","fault","repair","service issue","תקלה","לא עובד","לא עובדת","בעיה","תמיכה","תיקון","שירות","помощь","проблема","не работает","ремонт","مشكلة","لا يعمل","مساعدة","تصليح"],
    "installation": ["installation","install","installer","technician","field visit","setup","התקנה","להתקין","מתקין","טכנאי","ביקור טכנאי","установка","монтаж","تركيب","فني"],
    "appointments": ["appointment","meeting","callback","call back","consultation","schedule","תור","פגישה","שיחת חזרה","ייעוץ","לקבוע","זימון","консультация","встреча","звонок","موعد","استشارة","اتصال"],
    "enterprise": ["enterprise","company","branches","branch","national rollout","rollout","procurement","bulk","b2b","חברה","ארגוני","סניפים","רשת","פריסה ארצית","רכש","корпоратив","филиалы","شركة","فروع"],
    "sales": ["sales","quote","price","pricing","cost","buy","purchase","plan","הצעת מחיר","מחיר","כמה עולה","רכישה","לקנות","מסלול","стоимость","цена","купить","عرض سعر","سعر","شراء"],
    "urgent": ["urgent","emergency","asap","now","דחוף","חירום","עכשיו","מיידי","срочно","авария","طارئ","عاجل","الآن"],
}

@dataclass(frozen=True)
class Lead:
    """Incoming lead data used for routing."""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    message: Optional[str] = None
    language: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    product_interest: Optional[str] = None
    channel: Optional[str] = None
    budget: Optional[Union[int, float, str, Decimal]] = None
    is_urgent: bool = False
    consent_marketing: Optional[bool] = None
    created_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "Lead":
        known = set(cls.__dataclass_fields__.keys())
        kwargs: Dict[str, Any] = {}
        metadata: Dict[str, Any] = dict(data.get("metadata") or {})
        for key, value in data.items():
            if key in known and key != "metadata":
                kwargs[key] = value
            elif key not in known:
                metadata[key] = value
        kwargs["metadata"] = metadata
        if "is_urgent" in kwargs:
            kwargs["is_urgent"] = _to_bool(kwargs["is_urgent"])
        if "consent_marketing" in kwargs:
            kwargs["consent_marketing"] = _to_optional_bool(kwargs["consent_marketing"])
        return cls(**kwargs)

@dataclass(frozen=True)
class RoutingRule:
    """A deterministic routing rule."""
    name: str
    assignee: str
    department: str
    priority: str = "normal"
    sla_minutes: int = 120
    languages: Sequence[str] = field(default_factory=list)
    regions: Sequence[str] = field(default_factory=list)
    products: Sequence[str] = field(default_factory=list)
    channels: Sequence[str] = field(default_factory=list)
    urgent: Optional[bool] = None
    min_budget: Optional[Union[int, float, str, Decimal]] = None
    fallback: bool = False

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "RoutingRule":
        return cls(
            name=str(data["name"]),
            assignee=str(data["assignee"]),
            department=str(data["department"]),
            priority=str(data.get("priority", "normal")),
            sla_minutes=int(data.get("sla_minutes", 120)),
            languages=list(data.get("languages", []) or []),
            regions=list(data.get("regions", []) or []),
            products=list(data.get("products", []) or []),
            channels=list(data.get("channels", []) or []),
            urgent=data.get("urgent"),
            min_budget=data.get("min_budget"),
            fallback=bool(data.get("fallback", False)),
        )

@dataclass(frozen=True)
class RouteResult:
    """Output from a routing decision."""
    assignee: str
    department: str
    priority: str
    sla_minutes: int
    language: str
    region: str
    product_interest: str
    confidence: float
    reason_codes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    handoff_note: str = ""
    rule_name: str = ""
    normalized_phone: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, *, ensure_ascii: bool = False, indent: Optional[int] = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)

@dataclass(frozen=True)
class NormalizedLead:
    lead: Lead
    language: str
    region: str
    product_interest: str
    priority_hint: str
    normalized_phone: Optional[str]
    warnings: List[str]
    reason_codes: List[str]
    signals: Dict[str, Any]

def _clean_text(value: Any) -> str:
    return "" if value is None else str(value).strip()

def _lower(value: Any) -> str:
    return _clean_text(value).casefold()

def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().casefold() in {"1", "true", "yes", "y", "כן", "אמת"}

def _to_optional_bool(value: Any) -> Optional[bool]:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().casefold()
    if text in {"1", "true", "yes", "y", "כן", "אמת", "granted"}:
        return True
    if text in {"0", "false", "no", "n", "לא", "denied"}:
        return False
    return None

def _decimal(value: Any) -> Optional[Decimal]:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value).replace(",", ""))
    except (InvalidOperation, ValueError):
        return None

def _contains_any(text: str, aliases: Iterable[str]) -> bool:
    haystack = text.casefold()
    return any(alias.casefold() in haystack for alias in aliases if alias)

def normalize_language(explicit_language: Optional[str], text: str = "") -> Tuple[str, List[str], Dict[str, int]]:
    """Normalize a language hint and free text to HE/EN/RU/AR/UNKNOWN."""
    warnings: List[str] = []
    explicit_norm = LANGUAGE_ALIASES.get(_lower(explicit_language), "")
    counts = {
        "HE": len(re.findall(r"[\u0590-\u05FF]", text or "")),
        "AR": len(re.findall(r"[\u0600-\u06FF]", text or "")),
        "RU": len(re.findall(r"[\u0400-\u04FF]", text or "")),
        "EN": len(re.findall(r"[A-Za-z]", text or "")),
    }
    active_scripts = [lang for lang, count in counts.items() if count >= 2]
    detected = max(counts, key=counts.get) if any(counts.values()) else "UNKNOWN"
    if explicit_norm:
        if detected != "UNKNOWN" and explicit_norm != detected and active_scripts:
            warnings.append("LANGUAGE_CONFLICT")
        if len(active_scripts) > 1:
            warnings.append("LANGUAGE_MIXED")
        return explicit_norm, warnings, counts
    if len(active_scripts) > 1:
        warnings.append("LANGUAGE_MIXED")
    if detected == "EN" and _contains_any(text, ["precio", "bonjour", "instalación", "instalacion", "hola"]):
        warnings.append("UNSUPPORTED_LANGUAGE")
        return "UNKNOWN", warnings, counts
    return detected if detected in SUPPORTED_LANGUAGES else "UNKNOWN", warnings, counts

def normalize_phone(phone: Optional[str]) -> Tuple[Optional[str], List[str], Optional[str]]:
    """Normalize common Israeli phone numbers and infer weak region from landline prefixes."""
    raw = _clean_text(phone)
    if not raw:
        return None, [], None
    plus = raw.startswith("+")
    digits = re.sub(r"\D", "", raw)
    if not digits:
        return None, ["PHONE_INVALID"], None
    normalized: Optional[str] = None
    local = digits
    warnings: List[str] = []
    if plus and digits.startswith("972"):
        local = "0" + digits[3:]
        normalized = "+" + digits
    elif digits.startswith("972"):
        local = "0" + digits[3:]
        normalized = "+" + digits
    elif digits.startswith("0") and len(digits) in {9, 10}:
        local = digits
        normalized = "+972" + digits[1:]
    elif len(digits) == 9 and digits.startswith("5"):
        local = "0" + digits
        normalized = "+972" + digits
    else:
        warnings.append("PHONE_INVALID")
    area_region = None
    if local.startswith("02"):
        area_region = "JERUSALEM"
    elif local.startswith("03"):
        area_region = "CENTER"
    elif local.startswith("04"):
        area_region = "HAIFA"
    elif local.startswith("08"):
        area_region = "SOUTH"
    elif local.startswith("09"):
        area_region = "SHARON"
    return normalized, warnings, area_region

def normalize_region(region: Optional[str], city: Optional[str], text: str, phone_area_region: Optional[str]) -> Tuple[str, List[str], str]:
    """Normalize Israeli region from explicit field, city, text, and weak phone hint."""
    for source, value in [("explicit_region", region), ("city", city), ("message", text)]:
        value_cf = _clean_text(value).casefold()
        if not value_cf:
            continue
        for normalized, aliases in REGION_ALIASES.items():
            if value_cf == normalized.casefold() or _contains_any(value_cf, aliases):
                return normalized, [], source
    if phone_area_region:
        return phone_area_region, ["REGION_FROM_PHONE_WEAK"], "phone_area_code"
    return "UNKNOWN", ["UNKNOWN_REGION"], "none"

def normalize_product(product_interest: Optional[str], text: str) -> Tuple[str, List[str], str]:
    """Normalize product or department interest."""
    explicit = _clean_text(product_interest)
    combined = " ".join(part for part in [explicit, _clean_text(text)] if part)
    if not combined:
        return "general", ["UNKNOWN_PRODUCT"], "none"
    explicit_cf = explicit.casefold()
    for product, aliases in PRODUCT_ALIASES.items():
        if explicit_cf == product.casefold() or _contains_any(explicit_cf, aliases):
            return product, [], "explicit_product"
    for product in ["billing", "support", "installation", "appointments", "enterprise", "urgent", "sales"]:
        if _contains_any(combined, PRODUCT_ALIASES[product]):
            if product == "urgent" and _contains_any(combined, PRODUCT_ALIASES["support"]):
                return "support", [], "urgent_support_text"
            return product, [], "message"
    return "general", ["UNKNOWN_PRODUCT"], "none"

def determine_priority(lead: Lead, product: str, channel: Optional[str], budget: Optional[Decimal], warnings: List[str]) -> str:
    text = " ".join([_clean_text(lead.message), _clean_text(lead.product_interest)])
    urgent_text = _contains_any(text, PRODUCT_ALIASES["urgent"])
    if lead.is_urgent or product == "urgent" or (urgent_text and product == "support"):
        return "urgent"
    if budget is not None and budget >= Decimal("50000"):
        return "high"
    if product in {"support", "installation", "sales"} and _lower(channel) in {"whatsapp", "phone"}:
        return "high"
    if "MISSING_CONTACT" in warnings:
        return "low"
    return "normal"

def _lead_id_for(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(dict(payload), sort_keys=True, ensure_ascii=False, default=str)
    return "lead_" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def _read_store(path: Union[str, Path]) -> Dict[str, Any]:
    store_path = Path(path)
    if not store_path.exists():
        return {"leads": {}}
    data = json.loads(store_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("leads", {}), dict):
        raise ValueError("lead store must be a JSON object with a 'leads' object")
    data.setdefault("leads", {})
    return data


def _write_store(path: Union[str, Path], data: Mapping[str, Any]) -> None:
    store_path = Path(path)
    store_path.parent.mkdir(parents=True, exist_ok=True)
    store_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

class LeadRouterClient:
    """Deterministic lead router with sync and async methods."""

    def __init__(self, config: Optional[Mapping[str, Any]] = None) -> None:
        self.config: Dict[str, Any] = dict(config or default_config())
        self.rules: List[RoutingRule] = [RoutingRule.from_mapping(rule) for rule in self.config.get("rules", [])]
        errors = self.validate_config(self.config)
        if errors:
            raise ValueError("; ".join(errors))

    @classmethod
    def from_json_file(cls, path: Union[str, Path]) -> "LeadRouterClient":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    def create_lead(self, lead: Mapping[str, Any], store_path: Union[str, Path]) -> Dict[str, Any]:
        """Persist a lead payload in a local JSON store and return its generated ID."""
        payload = dict(lead)
        lead_id = _lead_id_for(payload)
        store = _read_store(store_path)
        store["leads"][lead_id] = payload
        _write_store(store_path, store)
        return {"lead_id": lead_id, "status": "created", "store_path": str(Path(store_path))}

    def get_lead(self, lead_id: str, store_path: Union[str, Path]) -> Dict[str, Any]:
        """Read a previously created lead payload from a local JSON store."""
        store = _read_store(store_path)
        try:
            lead = store["leads"][lead_id]
        except KeyError as exc:
            raise KeyError(f"lead_id not found: {lead_id}") from exc
        if not isinstance(lead, dict):
            raise ValueError(f"stored lead is not a JSON object: {lead_id}")
        return dict(lead)

    def route_stored_lead(self, lead_id: str, store_path: Union[str, Path]) -> RouteResult:
        """Route a lead that was previously saved with create_lead."""
        return self.route_lead(self.get_lead(lead_id, store_path))

    def route_lead(self, lead: Union[Lead, Mapping[str, Any]]) -> RouteResult:
        normalized = self.normalize_lead(lead)
        if "MISSING_CONTACT" in normalized.warnings:
            return self._data_quality_result(normalized)
        if normalized.language == "UNKNOWN" or "UNSUPPORTED_LANGUAGE" in normalized.warnings:
            name = "Urgent multilingual intake" if normalized.priority_hint == "urgent" else "Multilingual intake"
            return self._result_from_rule(self._find_rule_by_name(name), normalized, 75)
        scored_rules = [self._score_rule(rule, normalized, index) for index, rule in enumerate(self.rules)]
        scored_rules.sort(key=lambda item: (item[0], PRIORITY_ORDER.get(item[1].priority, 0), -item[1].sla_minutes), reverse=True)
        best_score, best_rule, _ = scored_rules[0]
        if best_score <= 1:
            best_rule = self._find_rule_by_name("Qualification fallback")
            best_score = 45
        result = self._result_from_rule(best_rule, normalized, best_score)
        if result.confidence < 0.55 and "LOW_CONFIDENCE" not in result.warnings:
            result = RouteResult(**{**result.to_dict(), "warnings": result.warnings + ["LOW_CONFIDENCE"]})
        return result

    async def aroute_lead(self, lead: Union[Lead, Mapping[str, Any]]) -> RouteResult:
        await asyncio.sleep(0)
        return self.route_lead(lead)

    def route_many(self, leads: Iterable[Union[Lead, Mapping[str, Any]]]) -> List[RouteResult]:
        return [self.route_lead(lead) for lead in leads]

    async def aroute_many(self, leads: Iterable[Union[Lead, Mapping[str, Any]]]) -> List[RouteResult]:
        return [await self.aroute_lead(lead) for lead in leads]

    def normalize_lead(self, lead: Union[Lead, Mapping[str, Any]]) -> NormalizedLead:
        lead_obj = lead if isinstance(lead, Lead) else Lead.from_mapping(lead)
        text = " ".join(_clean_text(part) for part in [lead_obj.name, lead_obj.message, lead_obj.city, lead_obj.region, lead_obj.product_interest] if _clean_text(part))
        normalized_phone, phone_warnings, phone_area_region = normalize_phone(lead_obj.phone)
        warnings: List[str] = list(phone_warnings)
        if not _clean_text(lead_obj.phone) and not _clean_text(lead_obj.email):
            warnings.append("MISSING_CONTACT")
        if lead_obj.consent_marketing is not True:
            warnings.append("MARKETING_CONSENT_MISSING")
        if isinstance(lead_obj.metadata, Mapping) and lead_obj.metadata.get("duplicate_risk"):
            warnings.append("DUPLICATE_RISK")
        language, language_warnings, language_counts = normalize_language(lead_obj.language, text)
        warnings.extend(language_warnings)
        region, region_warnings, region_source = normalize_region(lead_obj.region, lead_obj.city, text, phone_area_region)
        warnings.extend(region_warnings)
        product, product_warnings, product_source = normalize_product(lead_obj.product_interest, text)
        warnings.extend(product_warnings)
        budget = _decimal(lead_obj.budget)
        priority = determine_priority(lead_obj, product, lead_obj.channel, budget, warnings)
        reason_codes = []
        if language != "UNKNOWN":
            reason_codes.append(f"LANG_{language}")
        if region != "UNKNOWN":
            reason_codes.append(f"REGION_{region}")
        if product != "general":
            reason_codes.append(f"PRODUCT_{product.upper()}")
        if lead_obj.channel:
            reason_codes.append(f"CHANNEL_{_clean_text(lead_obj.channel).upper()}")
        return NormalizedLead(
            lead=lead_obj,
            language=language,
            region=region,
            product_interest=product,
            priority_hint=priority,
            normalized_phone=normalized_phone,
            warnings=list(dict.fromkeys(warnings)),
            reason_codes=reason_codes,
            signals={"language_counts": language_counts, "region_source": region_source, "product_source": product_source, "budget": str(budget) if budget is not None else None},
        )

    def explain(self, lead: Union[Lead, Mapping[str, Any]]) -> Dict[str, Any]:
        normalized = self.normalize_lead(lead)
        scored = sorted([self._score_rule(rule, normalized, index) for index, rule in enumerate(self.rules)], key=lambda item: item[0], reverse=True)
        return {
            "normalized": {
                "language": normalized.language,
                "region": normalized.region,
                "product_interest": normalized.product_interest,
                "priority_hint": normalized.priority_hint,
                "warnings": normalized.warnings,
                "reason_codes": normalized.reason_codes,
                "signals": normalized.signals,
            },
            "rules": [{"score": s, "rule": r.name, "assignee": r.assignee, "department": r.department, "priority": r.priority} for s, r, _ in scored],
            "selected": self.route_lead(normalized.lead).to_dict(),
        }

    @staticmethod
    def validate_config(config: Mapping[str, Any]) -> List[str]:
        errors: List[str] = []
        rules = config.get("rules", [])
        if not isinstance(rules, list) or not rules:
            return ["rules must be a non-empty list"]
        names = set()
        for idx, rule in enumerate(rules):
            prefix = f"rules[{idx}]"
            for field_name in ["name", "assignee", "department"]:
                if not rule.get(field_name):
                    errors.append(f"{prefix}.{field_name} is required")
            if rule.get("name") in names:
                errors.append(f"{prefix}.name duplicates another rule")
            names.add(rule.get("name"))
            if rule.get("priority", "normal") not in PRIORITY_ORDER:
                errors.append(f"{prefix}.priority must be one of {sorted(PRIORITY_ORDER)}")
            try:
                if int(rule.get("sla_minutes", 120)) <= 0:
                    errors.append(f"{prefix}.sla_minutes must be positive")
            except Exception:
                errors.append(f"{prefix}.sla_minutes must be an integer")
            for lang in rule.get("languages", []) or []:
                if str(lang).upper() not in SUPPORTED_LANGUAGES:
                    errors.append(f"{prefix}.languages contains unsupported value {lang!r}")
        required = {"Data quality", "Qualification fallback", "Multilingual intake", "Urgent multilingual intake"}
        existing = {str(rule.get("name")) for rule in rules}
        missing = required - existing
        if missing:
            errors.append(f"missing required fallback rules: {', '.join(sorted(missing))}")
        return errors

    def _find_rule_by_name(self, name: str) -> RoutingRule:
        for rule in self.rules:
            if rule.name == name:
                return rule
        raise ValueError(f"required rule not found: {name}")

    def _score_rule(self, rule: RoutingRule, normalized: NormalizedLead, index: int) -> Tuple[int, RoutingRule, int]:
        lead = normalized.lead
        score = 1 if rule.fallback else 0
        if rule.languages:
            if normalized.language in {str(lang).upper() for lang in rule.languages}:
                score += 20
            else:
                return -1000 + score, rule, index
        if rule.regions:
            if normalized.region in {str(region).upper() for region in rule.regions}:
                score += 25
            else:
                return -900 + score, rule, index
        if rule.products:
            if normalized.product_interest in {str(product).casefold() for product in rule.products}:
                score += 40
            else:
                return -800 + score, rule, index
        if rule.channels:
            if _lower(lead.channel) in {str(channel).casefold() for channel in rule.channels}:
                score += 5
            else:
                return -700 + score, rule, index
        if rule.urgent is not None:
            if bool(rule.urgent) == (normalized.priority_hint == "urgent"):
                score += 15
            else:
                return -600 + score, rule, index
        min_budget = _decimal(rule.min_budget)
        budget = _decimal(lead.budget)
        if min_budget is not None:
            if budget is not None and budget >= min_budget:
                score += 10
            else:
                return -500 + score, rule, index
        score += max(0, 5 - index // 10)
        return score, rule, index

    def _result_from_rule(self, rule: RoutingRule, normalized: NormalizedLead, score: int) -> RouteResult:
        priority = max(rule.priority, normalized.priority_hint, key=lambda p: PRIORITY_ORDER.get(p, 0))
        sla = min(rule.sla_minutes, _sla_for_priority(priority))
        warnings = list(dict.fromkeys(normalized.warnings))
        confidence = min(0.99, max(0.20, round(score / 95, 2)))
        return RouteResult(
            assignee=rule.assignee,
            department=rule.department,
            priority=priority,
            sla_minutes=sla,
            language=normalized.language,
            region=normalized.region,
            product_interest=normalized.product_interest,
            confidence=confidence,
            reason_codes=list(dict.fromkeys(normalized.reason_codes + [f"RULE_{_slug_code(rule.name)}"])),
            warnings=warnings,
            handoff_note=build_handoff_note(language=normalized.language, region=normalized.region, product=normalized.product_interest, priority=priority, sla_minutes=sla, warnings=warnings),
            rule_name=rule.name,
            normalized_phone=normalized.normalized_phone,
        )

    def _data_quality_result(self, normalized: NormalizedLead) -> RouteResult:
        rule = self._find_rule_by_name("Data quality")
        warnings = list(dict.fromkeys(normalized.warnings + ["MISSING_CONTACT"]))
        return RouteResult(
            assignee=rule.assignee,
            department=rule.department,
            priority="low",
            sla_minutes=rule.sla_minutes,
            language=normalized.language,
            region=normalized.region,
            product_interest=normalized.product_interest,
            confidence=0.99,
            reason_codes=list(dict.fromkeys(normalized.reason_codes + ["RULE_DATA_QUALITY"])),
            warnings=warnings,
            handoff_note="Lead lacks a usable phone or email. Request contact details before routing to a sales or service queue.",
            rule_name=rule.name,
            normalized_phone=normalized.normalized_phone,
        )

def _sla_for_priority(priority: str) -> int:
    return {"urgent": 10, "high": 30, "normal": 120, "low": 1440}.get(priority, 120)

def _slug_code(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").upper() or "UNKNOWN"

def build_handoff_note(*, language: str, region: str, product: str, priority: str, sla_minutes: int, warnings: Sequence[str]) -> str:
    language_sentence = {
        "HE": "Reply in Hebrew.",
        "EN": "Reply in English.",
        "RU": "Reply in Russian.",
        "AR": "Reply in Arabic.",
        "UNKNOWN": "Use multilingual intake and preserve the original message.",
    }.get(language, "Use multilingual intake and preserve the original message.")
    parts = [
        f"{language} lead from {region} about {product}.",
        language_sentence,
        f"First response within {sla_minutes} minutes.",
    ]
    if priority == "urgent":
        parts.append("Treat as urgent and attempt phone callback first when a phone number is available.")
    if "MARKETING_CONSENT_MISSING" in warnings:
        parts.append("Marketing follow-up is not allowed without consent.")
    if "UNKNOWN_REGION" in warnings:
        parts.append("Confirm service location.")
    if "LANGUAGE_MIXED" in warnings:
        parts.append("Message contains mixed language; keep original text visible.")
    return " ".join(parts)

def default_config() -> Dict[str, Any]:
    """Return the default routing rules."""
    return {
        "version": "1.2.0",
        "rules": [
            {"name": "Data quality", "assignee": "Data Quality Queue", "department": "data_quality", "priority": "low", "sla_minutes": 1440, "fallback": True},
            {"name": "Urgent multilingual intake", "assignee": "Multilingual Urgent Intake", "department": "urgent_intake", "priority": "urgent", "sla_minutes": 10, "urgent": True},
            {"name": "Russian support", "assignee": "Russian Support Queue", "department": "support", "priority": "high", "sla_minutes": 30, "languages": ["RU"], "products": ["support"]},
            {"name": "Arabic sales north", "assignee": "Arabic Sales Queue", "department": "sales", "priority": "normal", "sla_minutes": 120, "languages": ["AR"], "regions": ["NORTH", "HAIFA"], "products": ["sales", "installation"]},
            {"name": "Arabic support", "assignee": "Arabic Support Queue", "department": "support", "priority": "high", "sla_minutes": 30, "languages": ["AR"], "products": ["support"]},
            {"name": "North installations", "assignee": "North Service Queue", "department": "installation", "priority": "high", "sla_minutes": 30, "regions": ["NORTH", "HAIFA"], "products": ["installation"]},
            {"name": "Center installations", "assignee": "Center Service Queue", "department": "installation", "priority": "high", "sla_minutes": 30, "regions": ["CENTER", "SHARON"], "products": ["installation"]},
            {"name": "Jerusalem installations", "assignee": "Jerusalem Service Queue", "department": "installation", "priority": "high", "sla_minutes": 30, "regions": ["JERUSALEM", "WEST_BANK"], "products": ["installation"]},
            {"name": "South installations", "assignee": "South Service Queue", "department": "installation", "priority": "high", "sla_minutes": 45, "regions": ["SOUTH", "EILAT"], "products": ["installation"]},
            {"name": "Billing", "assignee": "Billing Queue", "department": "billing", "priority": "normal", "sla_minutes": 240, "products": ["billing"]},
            {"name": "Enterprise", "assignee": "Enterprise Desk", "department": "enterprise", "priority": "high", "sla_minutes": 60, "products": ["enterprise"]},
            {"name": "High budget sales", "assignee": "Senior Sales Queue", "department": "sales", "priority": "high", "sla_minutes": 60, "products": ["sales"], "min_budget": 50000},
            {"name": "Hebrew sales center", "assignee": "Center Sales Queue", "department": "sales", "priority": "normal", "sla_minutes": 120, "languages": ["HE"], "regions": ["CENTER", "SHARON"], "products": ["sales"]},
            {"name": "Hebrew sales north", "assignee": "North Sales Queue", "department": "sales", "priority": "normal", "sla_minutes": 120, "languages": ["HE"], "regions": ["NORTH", "HAIFA"], "products": ["sales"]},
            {"name": "General support", "assignee": "Support Queue", "department": "support", "priority": "high", "sla_minutes": 60, "products": ["support"]},
            {"name": "Appointments", "assignee": "Appointments Queue", "department": "appointments", "priority": "normal", "sla_minutes": 120, "products": ["appointments"]},
            {"name": "General sales", "assignee": "Sales Qualification Queue", "department": "sales", "priority": "normal", "sla_minutes": 120, "products": ["sales"]},
            {"name": "Multilingual intake", "assignee": "Multilingual Intake Queue", "department": "qualification", "priority": "normal", "sla_minutes": 120, "fallback": True},
            {"name": "Qualification fallback", "assignee": "Qualification Queue", "department": "qualification", "priority": "normal", "sla_minutes": 120, "fallback": True},
        ],
    }

def load_json_or_jsonl(path: Union[str, Path]) -> List[Dict[str, Any]]:
    text = Path(path).read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text.startswith("["):
        return json.loads(text)
    return [json.loads(line) for line in text.splitlines() if line.strip()]

def load_csv(path: Union[str, Path]) -> List[Dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]

def write_jsonl(path: Union[str, Path], results: Iterable[RouteResult]) -> None:
    with Path(path).open("w", encoding="utf-8") as handle:
        for result in results:
            handle.write(result.to_json(indent=None) + "\n")

def route_csv(input_path: Union[str, Path], output_path: Union[str, Path], config_path: Optional[Union[str, Path]] = None) -> List[RouteResult]:
    client = LeadRouterClient.from_json_file(config_path) if config_path else LeadRouterClient()
    results = client.route_many(load_csv(input_path))
    write_jsonl(output_path, results)
    return results

__all__ = [
    "Lead", "RoutingRule", "RouteResult", "NormalizedLead", "LeadRouterClient", "default_config",
    "normalize_language", "normalize_phone", "normalize_region", "normalize_product",
    "route_csv", "load_csv", "load_json_or_jsonl", "write_jsonl",
]
