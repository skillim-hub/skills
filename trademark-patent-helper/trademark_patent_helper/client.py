"""Structured helper client for Israeli trademark and patent filing preparation.

The module performs local validation and structured triage. It does not submit
filings, scrape official systems, or provide legal advice.
"""

from __future__ import annotations

import asyncio
import dataclasses
import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Literal


RiskLevel = Literal["green", "yellow", "red"]
Kind = Literal["trademark", "patent", "unknown"]
Environment = Literal["sandbox", "production"]


DESCRIPTIVE_TERMS_EN = {
    "best", "fast", "quick", "cheap", "premium", "quality", "tax", "refund",
    "refunds", "accounting", "cafe", "coffee", "cosmetics", "dead", "sea",
    "israel", "israeli", "shop", "store", "online", "digital", "smart",
    "healthy", "natural", "fresh", "clean", "security", "pay", "fitness",
}
DESCRIPTIVE_TERMS_HE = {
    "מהיר", "מהירה", "מהירים", "הכי", "טוב", "טובה", "זול", "זולה", "איכותי",
    "מס", "החזר", "החזרי", "קפה", "ים", "המלח", "קוסמטיקה", "חנות", "מקוון",
    "דיגיטלי", "חכם", "חכמה", "בריא", "טבעי", "טרי", "נקי", "אבטחה", "כושר",
}
REGULATED_TERMS = {
    "medical", "medicine", "pharma", "cannabis", "security", "defense", "finance",
    "bank", "payment", "crypto", "insurance", "clinic", "therapy", "רפואי",
    "רפואה", "קנאביס", "אבטחה", "ביטחון", "פיננסי", "בנק", "תשלום", "ביטוח",
}
OWNERSHIP_RISK_TERMS = {
    "employee", "employer", "work", "job", "contractor", "client", "university",
    "hospital", "founder", "founders", "עובד", "מעסיק", "עבודה", "פרילנסר",
    "לקוח", "אוניברסיטה", "בית חולים", "מייסד", "מייסדים",
}


@dataclass(slots=True)
class ClassItem:
    """Trademark class entry."""

    class_no: int
    items: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ClassItem":
        return cls(class_no=int(data["class_no"]), items=[str(x) for x in data.get("items", [])])


@dataclass(slots=True)
class Disclosure:
    """Patent disclosure event."""

    date: str
    channel: str
    details: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Disclosure":
        return cls(
            date=str(data.get("date", "")),
            channel=str(data.get("channel", "")),
            details=str(data.get("details", "")),
        )


@dataclass(slots=True)
class Assessment:
    """Structured helper result."""

    kind: Kind
    risk_level: RiskLevel
    issues: list[str] = field(default_factory=list)
    issue_codes: list[str] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    classes: list[dict[str, Any]] = field(default_factory=list)
    summary: str = ""
    request_id: str | None = None
    environment: Environment = "sandbox"

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def to_json(self, *, indent: int = 2, ensure_ascii: bool = False) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=ensure_ascii)

    def to_markdown(self) -> str:
        parts = [
            f"# {self.kind.title()} assessment",
            "",
            f"Risk level: **{self.risk_level}**",
        ]
        if self.request_id:
            parts.extend(["", f"Request ID: `{self.request_id}`"])
        if self.summary:
            parts.extend(["", self.summary])
        if self.issues:
            parts.extend(["", "## Issues"])
            parts.extend([f"- {issue}" for issue in self.issues])
        if self.issue_codes:
            parts.extend(["", "## Issue codes"])
            parts.extend([f"- `{code}`" for code in self.issue_codes])
        if self.classes:
            parts.extend(["", "## Classes"])
            for entry in self.classes:
                parts.append(f"- Class {entry.get('class_no')}: {entry.get('filing_text', '')}")
        if self.next_steps:
            parts.extend(["", "## Next steps"])
            parts.extend([f"- {step}" for step in self.next_steps])
        if self.warnings:
            parts.extend(["", "## Warnings"])
            parts.extend([f"- {warning}" for warning in self.warnings])
        return "\n".join(parts).strip() + "\n"


class FilingHelperClient:
    """Local structured CLI/client for trademark and patent preparation."""

    def __init__(self, environment: Environment = "sandbox") -> None:
        if environment not in {"sandbox", "production"}:
            raise ValueError("environment must be sandbox or production")
        self.environment = environment

    def assess(self, payload: dict[str, Any]) -> Assessment:
        kind = str(payload.get("kind", "")).strip().lower()
        if not kind:
            inferred = self.classify_asset(payload)
            if inferred != "unknown":
                payload = {**payload, "kind": inferred}
                kind = inferred
            else:
                return Assessment(
                    kind="unknown",
                    risk_level="yellow",
                    issues=["The asset type is missing."],
                    issue_codes=["MISSING_KIND"],
                    next_steps=["Set kind to trademark or patent, or provide enough facts to classify the asset."],
                    environment=self.environment,
                )

        if kind == "trademark":
            return self.assess_trademark(payload)
        if kind == "patent":
            return self.assess_patent(payload)
        return Assessment(
            kind="unknown",
            risk_level="yellow",
            issues=[f"Unsupported kind: {kind}."],
            issue_codes=["UNKNOWN_KIND"],
            next_steps=["Use trademark or patent, or run intake to classify the asset."],
            environment=self.environment,
        )

    async def assess_async(self, payload: dict[str, Any]) -> Assessment:
        await asyncio.sleep(0)
        return self.assess(payload)

    def create(self, payload: dict[str, Any], *, state_path: str | Path | None = None) -> Assessment:
        assessment = self.assess(payload)
        request_id = str(uuid.uuid4())
        assessment.request_id = request_id
        store = self._load_store(state_path)
        store[request_id] = {
            "payload": payload,
            "assessment": assessment.to_dict(),
        }
        self._save_store(store, state_path)
        return assessment

    def get(self, request_id: str, *, state_path: str | Path | None = None) -> Assessment:
        store = self._load_store(state_path)
        if request_id not in store:
            return Assessment(
                kind="unknown",
                risk_level="yellow",
                issues=[f"No saved request found for ID {request_id}."],
                issue_codes=["NOT_FOUND"],
                next_steps=["Check the ID from the create response and the selected state file."],
                request_id=request_id,
                environment=self.environment,
            )
        data = store[request_id]["assessment"]
        return Assessment(**data)

    def classify_asset(self, payload: dict[str, Any]) -> Kind:
        text = " ".join(str(v) for v in payload.values() if not isinstance(v, (dict, list))).lower()
        if any(k in text for k in ["mark", "brand", "slogan", "trademark", "מותג", "סימן"]):
            return "trademark"
        if any(k in text for k in ["invention", "technical", "prototype", "patent", "device", "method", "המצאה", "פטנט", "טכני"]):
            return "patent"
        return "unknown"

    def assess_trademark(self, payload: dict[str, Any]) -> Assessment:
        issues: list[str] = []
        codes: list[str] = []
        steps: list[str] = [
            "Search identical, phonetic, Hebrew, English, and transliteration variants in the Israel trademark database.",
            "Verify current official forms, fees, and goods/services wording before filing.",
            "Save filing receipt, application number, and official correspondence.",
        ]
        warnings: list[str] = ["Registration is not guaranteed and depends on examination and earlier rights."]
        classes_output: list[dict[str, Any]] = []

        mark = str(payload.get("mark_text") or payload.get("mark") or "").strip()
        mark_type = str(payload.get("mark_type") or "").strip().lower()
        if not mark and "logo" not in mark_type:
            issues.append("Trademark request lacks exact mark wording or a clear visual-sign description.")
            codes.append("MISSING_MARK")

        raw_classes = payload.get("classes") or []
        class_items: list[ClassItem] = []
        if raw_classes:
            for item in raw_classes:
                ci = ClassItem.from_dict(item)
                if ci.class_no < 1 or ci.class_no > 45:
                    issues.append(f"Class {ci.class_no} is outside the valid Nice Classification range 1-45.")
                    codes.append("INVALID_CLASS")
                else:
                    class_items.append(ci)
                    classes_output.append({
                        "class_no": ci.class_no,
                        "filing_text": "; ".join(ci.items),
                    })
        else:
            goods_services = payload.get("goods_services") or payload.get("services") or payload.get("goods")
            if not goods_services:
                issues.append("Trademark request lacks goods/services or class information.")
                codes.append("MISSING_CLASSES")
            else:
                steps.append("Map the plain-language goods/services to Nice classes before filing.")

        if self.is_descriptive_mark(mark, payload):
            issues.append("The mark appears descriptive or laudatory for the listed goods/services.")
            codes.append("DESCRIPTIVE_MARK")
            steps.insert(0, "Consider adopting a more distinctive mark or preparing acquired-distinctiveness evidence.")

        if len(class_items) >= 6:
            issues.append("The request contains many classes; overbroad filings increase cost and may not match real use.")
            codes.append("BROAD_CLASSES")
            steps.append("Remove speculative classes and keep only real or bona fide planned goods/services.")

        if self.contains_regulated_terms(payload):
            issues.append("The goods/services appear regulated or sensitive.")
            codes.append("REGULATED_FIELD")
            steps.append("Check sector-specific legal restrictions before filing or marketing.")

        if any(ci.class_no == 35 for ci in class_items):
            steps.append("Use Class 35 only for real retail, marketplace, advertising, or business services, not as a substitute for product classes.")
        if any(ci.class_no == 42 for ci in class_items):
            steps.append("For SaaS, use Class 42 for non-downloadable software; use Class 9 only for downloadable software.")

        risk = self.combine_risk(codes)
        summary = f"Trademark preparation for {mark or 'the described sign'}."
        return Assessment(
            kind="trademark",
            risk_level=risk,
            issues=issues,
            issue_codes=codes,
            next_steps=dedupe(steps),
            warnings=warnings,
            classes=classes_output,
            summary=summary,
            environment=self.environment,
        )

    def assess_patent(self, payload: dict[str, Any]) -> Assessment:
        issues: list[str] = []
        codes: list[str] = []
        steps: list[str] = [
            "Do not disclose publicly before filing strategy is confirmed.",
            "Prepare an invention disclosure with technical field, problem, solution, alternatives, drawings, and advantages.",
            "Run a prior-art search across patent databases and non-patent sources.",
            "Ask a patent attorney to review patentability and draft claims when commercial value matters.",
            "Verify current official filing requirements and fees before submission.",
        ]
        warnings: list[str] = [
            "Patentability requires novelty, utility, and inventive step.",
            "This helper does not submit applications or replace professional drafting.",
        ]

        title = str(payload.get("title") or payload.get("invention_title") or "").strip()
        if not title:
            issues.append("Patent request lacks a concise technical title.")
            codes.append("MISSING_TITLE")

        solution = str(payload.get("solution") or payload.get("technical_solution") or payload.get("description") or "").strip()
        novel_features = payload.get("novel_features") or payload.get("new_features") or []
        if isinstance(novel_features, str):
            novel_features = [novel_features] if novel_features.strip() else []
        if not solution or len(solution.split()) < 8:
            issues.append("Patent request lacks concrete technical implementation details.")
            codes.append("MISSING_TECHNICAL_DETAIL")
        if not novel_features:
            issues.append("Patent request does not identify concrete novel technical features.")
            codes.append("NO_NOVEL_FEATURES")

        disclosures = [Disclosure.from_dict(d) for d in payload.get("public_disclosures", [])]
        if disclosures:
            issues.append("Public disclosure was reported; novelty rights may be at risk.")
            codes.append("PUBLIC_DISCLOSURE")
            steps.insert(0, "Build a disclosure timeline with date, channel, audience, confidentiality terms, and exact material disclosed.")

        if self.has_ownership_risk(payload):
            issues.append("Ownership facts suggest employee, contractor, founder, university, or client-related risk.")
            codes.append("OWNERSHIP_RISK")
            steps.append("Review employment, contractor, founder-assignment, university, hospital, and funding agreements before filing.")

        if self.contains_regulated_terms(payload):
            issues.append("The invention appears to involve a regulated or sensitive field.")
            codes.append("REGULATED_FIELD")
            steps.append("Coordinate patent strategy with regulatory and sector-specific legal review.")

        if self.looks_like_business_method(payload):
            issues.append("The description may be a business method or commercial concept without enough technical detail.")
            codes.append("BUSINESS_METHOD_RISK")
            steps.append("Identify the concrete technical problem, technical architecture, and measurable technical effect.")

        risk = self.combine_risk(codes)
        summary = f"Patent preparation for {title or 'the described invention'}."
        return Assessment(
            kind="patent",
            risk_level=risk,
            issues=issues,
            issue_codes=codes,
            next_steps=dedupe(steps),
            warnings=warnings,
            summary=summary,
            environment=self.environment,
        )

    def is_descriptive_mark(self, mark: str, payload: dict[str, Any]) -> bool:
        if not mark:
            return False
        words = tokenize(mark)
        if not words:
            return False
        descriptive_count = sum(1 for w in words if w in DESCRIPTIVE_TERMS_EN or w in DESCRIPTIVE_TERMS_HE)
        if descriptive_count >= max(1, len(words) // 2):
            return True
        meaning = str(payload.get("meaning") or "").lower()
        return any(term in meaning for term in ["describe", "descriptive", "תיאורי", "מתאר"])

    def contains_regulated_terms(self, payload: dict[str, Any]) -> bool:
        text = flatten_text(payload).lower()
        return any(term in text for term in REGULATED_TERMS)

    def has_ownership_risk(self, payload: dict[str, Any]) -> bool:
        text = flatten_text(payload).lower()
        return any(term in text for term in OWNERSHIP_RISK_TERMS)

    def looks_like_business_method(self, payload: dict[str, Any]) -> bool:
        text = flatten_text(payload).lower()
        business_terms = ["subscription", "pricing", "marketplace", "advertising", "business model", "gym", "מנוי", "תמחור", "מודל עסקי"]
        technical_terms = ["sensor", "controller", "processor", "memory", "valve", "circuit", "database", "encryption", "network", "חיישן", "בקר", "מעבד"]
        return any(t in text for t in business_terms) and not any(t in text for t in technical_terms)

    def combine_risk(self, codes: Iterable[str]) -> RiskLevel:
        codes_set = set(codes)
        red_codes = {
            "PUBLIC_DISCLOSURE", "DESCRIPTIVE_MARK", "INVALID_CLASS",
            "MISSING_MARK", "MISSING_CLASSES", "MISSING_TECHNICAL_DETAIL",
            "NO_NOVEL_FEATURES",
        }
        yellow_codes = {"OWNERSHIP_RISK", "REGULATED_FIELD", "BROAD_CLASSES", "BUSINESS_METHOD_RISK", "MISSING_TITLE"}
        if codes_set & red_codes:
            return "red"
        if codes_set & yellow_codes:
            return "yellow"
        return "green"

    def default_state_path(self) -> Path:
        return Path.home() / ".trademark_patent_helper" / f"{self.environment}-records.json"

    def _load_store(self, state_path: str | Path | None = None) -> dict[str, Any]:
        path = Path(state_path) if state_path else self.default_state_path()
        if not path.exists():
            return {}
        return json.loads(path.read_text(encoding="utf-8"))

    def _save_store(self, store: dict[str, Any], state_path: str | Path | None = None) -> None:
        path = Path(state_path) if state_path else self.default_state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")


def tokenize(text: str) -> list[str]:
    return re.findall(r"[A-Za-z]+|[\u0590-\u05FF]+", text.lower())


def flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(flatten_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(flatten_text(v) for v in value)
    return str(value)


def dedupe(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def normalize_il_date(value: str) -> str:
    """Normalize common ISO, slash, or hyphen dates to DD/MM/YYYY where possible."""

    value = value.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt).strftime("%d/%m/%Y")
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def assess_file(path: str | Path, *, environment: Environment = "sandbox") -> Assessment:
    return FilingHelperClient(environment=environment).assess(load_json(path))


__all__ = [
    "Assessment",
    "ClassItem",
    "Disclosure",
    "Environment",
    "FilingHelperClient",
    "assess_file",
    "dedupe",
    "flatten_text",
    "load_json",
    "normalize_il_date",
    "tokenize",
]
