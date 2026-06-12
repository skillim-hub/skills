"""Typed RTL UI audit client for HTML, CSS, Tailwind, and Israeli localization checks."""

from __future__ import annotations

import asyncio
import json
import re
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Literal, Sequence

Severity = Literal["high", "medium", "low"]
Direction = Literal["rtl", "ltr", "auto"]
AuditKind = Literal["html", "css", "tailwind"]
Environment = Literal["sandbox", "production"]

RTL_RE = re.compile(r"[\u0590-\u05FF\u0600-\u06FF]")
LTR_RE = re.compile(r"[A-Za-z]")
HTML_TAG_RE = re.compile(r"<html\b[^>]*>", re.IGNORECASE)
INPUT_RE = re.compile(r"<input\b[^>]*>", re.IGNORECASE)
TEXTAREA_RE = re.compile(r"<textarea\b[^>]*>", re.IGNORECASE)
ATTR_RE = re.compile(r"([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(['\"])(.*?)\2")
CLASS_RE = re.compile(r"\bclass\s*=\s*(['\"])(.*?)\1", re.IGNORECASE | re.DOTALL)

PHYSICAL_CSS_PATTERNS: dict[str, tuple[str, str]] = {
    "margin-left": ("CSS_PHYSICAL_DIRECTION", "Use margin-inline-start or margin-inline-end after semantic review."),
    "margin-right": ("CSS_PHYSICAL_DIRECTION", "Use margin-inline-end or margin-inline-start after semantic review."),
    "padding-left": ("CSS_PHYSICAL_DIRECTION", "Use padding-inline-start."),
    "padding-right": ("CSS_PHYSICAL_DIRECTION", "Use padding-inline-end."),
    "border-left": ("CSS_PHYSICAL_DIRECTION", "Use border-inline-start."),
    "border-right": ("CSS_PHYSICAL_DIRECTION", "Use border-inline-end."),
    "left": ("CSS_PHYSICAL_DIRECTION", "Use inset-inline-start when the side is logical start."),
    "right": ("CSS_PHYSICAL_DIRECTION", "Use inset-inline-end when the side is logical end."),
    "float: left": ("CSS_PHYSICAL_FLOAT", "Use flex or grid and logical alignment."),
    "float: right": ("CSS_PHYSICAL_FLOAT", "Use flex or grid and logical alignment."),
    "text-align: left": ("CSS_PHYSICAL_TEXT_ALIGN", "Use text-align: start or end by meaning."),
    "text-align: right": ("CSS_PHYSICAL_TEXT_ALIGN", "Use text-align: start for default RTL paragraphs or end for trailing alignment."),
}

CSS_REPLACEMENTS: dict[str, str] = {
    "margin-left": "margin-inline-start",
    "margin-right": "margin-inline-end",
    "padding-left": "padding-inline-start",
    "padding-right": "padding-inline-end",
    "border-left": "border-inline-start",
    "border-right": "border-inline-end",
    "text-align: left": "text-align: start",
    "text-align: right": "text-align: start",
}

TAILWIND_PREFIXES: tuple[tuple[str, str, str, Severity], ...] = (
    ("ml-", "TW_PHYSICAL_MARGIN", "Use ms-* or me-* after checking whether the space belongs to inline start or inline end.", "medium"),
    ("mr-", "TW_PHYSICAL_MARGIN", "Use me-* or ms-* after checking whether the space belongs to inline end or inline start.", "medium"),
    ("pl-", "TW_PHYSICAL_PADDING", "Use ps-* for padding inline start.", "medium"),
    ("pr-", "TW_PHYSICAL_PADDING", "Use pe-* for padding inline end.", "medium"),
    ("left-", "TW_PHYSICAL_INSET", "Use start-* when the side is logical inline start.", "medium"),
    ("right-", "TW_PHYSICAL_INSET", "Use end-* when the side is logical inline end.", "medium"),
    ("border-l", "TW_PHYSICAL_BORDER", "Use border-s* for inline start borders.", "medium"),
    ("border-r", "TW_PHYSICAL_BORDER", "Use border-e* for inline end borders.", "medium"),
    ("rounded-l", "TW_PHYSICAL_RADIUS", "Review logical corner intent; use direction variants if needed.", "low"),
    ("rounded-r", "TW_PHYSICAL_RADIUS", "Review logical corner intent; use direction variants if needed.", "low"),
    ("origin-left", "TW_PHYSICAL_ORIGIN", "Use direction-specific transform origin when needed.", "low"),
    ("origin-right", "TW_PHYSICAL_ORIGIN", "Use direction-specific transform origin when needed.", "low"),
    ("space-x-", "TW_SPACE_X", "Prefer gap-* for direction-safe spacing.", "low"),
)

TAILWIND_EXACT: dict[str, tuple[str, str, Severity]] = {
    "text-left": ("TW_PHYSICAL_TEXT_ALIGN", "Use text-start or text-end.", "medium"),
    "text-right": ("TW_PHYSICAL_TEXT_ALIGN", "Use text-start or text-end.", "medium"),
    "float-left": ("TW_PHYSICAL_FLOAT", "Use flex or grid layout instead of float.", "low"),
    "float-right": ("TW_PHYSICAL_FLOAT", "Use flex or grid layout instead of float.", "low"),
    "clear-left": ("TW_PHYSICAL_FLOAT", "Use modern layout primitives.", "low"),
    "clear-right": ("TW_PHYSICAL_FLOAT", "Use modern layout primitives.", "low"),
    "flex-row-reverse": ("TW_ROW_REVERSE", "Do not use as a global RTL fix; verify reading and keyboard order.", "low"),
}


@dataclass(frozen=True)
class AuditIssue:
    severity: Severity
    code: str
    message: str
    recommendation: str
    line: int | None = None
    evidence: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class AuditResult:
    issues: tuple[AuditIssue, ...]

    @property
    def summary(self) -> dict[str, int]:
        counts = {"total": len(self.issues), "high": 0, "medium": 0, "low": 0}
        for issue in self.issues:
            counts[issue.severity] += 1
        return counts

    def to_dict(self) -> dict[str, object]:
        return {"summary": self.summary, "issues": [issue.to_dict() for issue in self.issues]}

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def to_markdown(self) -> str:
        if not self.issues:
            return "No RTL issues detected by the static audit."
        lines = [
            "| Severity | Code | Line | Evidence | Recommendation |",
            "|---|---|---:|---|---|",
        ]
        for issue in self.issues:
            line = "" if issue.line is None else str(issue.line)
            evidence = (issue.evidence or "").replace("|", "\\|").replace("\n", " ")
            lines.append(
                f"| {issue.severity} | `{issue.code}` | {line} | `{evidence}` | {issue.recommendation} |"
            )
        return "\n".join(lines)


@dataclass(frozen=True)
class AuditRecord:
    id: str
    kind: AuditKind
    env: Environment
    created_at: str
    result: AuditResult

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "kind": self.kind,
            "env": self.env,
            "created_at": self.created_at,
            "result": self.result.to_dict(),
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "AuditRecord":
        result_data = data.get("result", {})
        issues_data = result_data.get("issues", []) if isinstance(result_data, dict) else []
        issues = tuple(AuditIssue(**issue) for issue in issues_data)
        return cls(
            id=str(data["id"]),
            kind=str(data["kind"]),  # type: ignore[arg-type]
            env=str(data["env"]),  # type: ignore[arg-type]
            created_at=str(data["created_at"]),
            result=AuditResult(issues),
        )


def _line_number(text: str, start: int) -> int:
    return text.count("\n", 0, start) + 1


def _attrs(tag: str) -> dict[str, str]:
    return {match.group(1).lower(): match.group(3) for match in ATTR_RE.finditer(tag)}


def infer_direction(text: str) -> Direction:
    """Infer direction from the first strong Hebrew, Arabic, or Latin character."""
    for char in text:
        if RTL_RE.match(char):
            return "rtl"
        if LTR_RE.match(char):
            return "ltr"
    return "auto"


def recommended_input_dir(field_type: str, name: str = "") -> Direction:
    """Return the recommended direction for a form input type or semantic field name."""
    field_type = (field_type or "text").lower()
    name = name.lower()
    ltr_types = {"email", "url", "tel", "number"}
    ltr_names = (
        "phone", "mobile", "email", "url", "amount", "price", "id", "sku", "code",
        "vat", "tax", "bank", "account", "iban", "invoice", "order"
    )
    if field_type in ltr_types or any(token in name for token in ltr_names):
        return "ltr"
    return "auto"


def recommend_input_attributes(field_type: str, name: str = "") -> dict[str, str]:
    """Recommend HTML input attributes for RTL-safe editing."""
    direction = recommended_input_dir(field_type, name)
    attrs = {"dir": direction}
    if field_type.lower() == "tel" or "phone" in name.lower() or "mobile" in name.lower():
        attrs["inputmode"] = "tel"
        attrs["autocomplete"] = "tel"
    elif field_type.lower() == "email" or "email" in name.lower():
        attrs["autocomplete"] = "email"
    elif "amount" in name.lower() or "price" in name.lower():
        attrs["inputmode"] = "decimal"
    elif "id" in name.lower() or "number" in name.lower():
        attrs["inputmode"] = "numeric"
    return attrs


def validate_israeli_id(value: str) -> bool:
    """Validate a 5-9 digit Israeli ID checksum."""
    digits = re.sub(r"\s+", "", value)
    if not digits.isdigit() or not (5 <= len(digits) <= 9):
        return False
    digits = digits.zfill(9)
    total = 0
    for index, char in enumerate(digits):
        num = int(char) * (1 if index % 2 == 0 else 2)
        total += num if num < 10 else num - 9
    return total % 10 == 0


def format_dd_mm_yyyy(year: int, month: int, day: int) -> str:
    """Format a date-like triple as DD/MM/YYYY."""
    return f"{day:02d}/{month:02d}/{year:04d}"


def merge_results(results: Iterable[AuditResult]) -> AuditResult:
    issues: list[AuditIssue] = []
    for result in results:
        issues.extend(result.issues)
    return AuditResult(tuple(issues))


class RtlAuditClient:
    """Sync and async helper for static RTL checks."""

    def __init__(self, store_dir: str | Path | None = None) -> None:
        self.store_dir = Path(store_dir) if store_dir is not None else Path(".rtl-advisor-audits")

    def audit_html(self, source: str) -> AuditResult:
        issues: list[AuditIssue] = []

        html_match = HTML_TAG_RE.search(source)
        if html_match:
            html_tag = html_match.group(0)
            attrs = _attrs(html_tag)
            line = _line_number(source, html_match.start())
            if "dir" not in attrs:
                issues.append(AuditIssue("high", "HTML_DIR_MISSING", "Root html element has no dir attribute.", 'Set <html lang="he" dir="rtl"> or derive lang and dir from locale.', line, html_tag))
            if "lang" not in attrs:
                issues.append(AuditIssue("medium", "HTML_LANG_MISSING", "Root html element has no lang attribute.", 'Set lang="he", lang="ar", or the active locale.', line, html_tag))
            if attrs.get("dir") == "rtl" and attrs.get("lang", "").lower().startswith("en"):
                issues.append(AuditIssue("medium", "HTML_LANG_DIR_MISMATCH", "The page is RTL but the root language is English.", "Use a Hebrew or Arabic language tag, or change direction for English pages.", line, html_tag))
        else:
            issues.append(AuditIssue("medium", "HTML_ROOT_NOT_FOUND", "No root html element was found.", "Audit the root layout and set lang and dir at the highest stable boundary."))

        for match in INPUT_RE.finditer(source):
            tag = match.group(0)
            attrs = _attrs(tag)
            line = _line_number(source, match.start())
            input_type = attrs.get("type", "text").lower()
            name = attrs.get("name", attrs.get("id", ""))
            expected = recommended_input_dir(input_type, name)
            actual = attrs.get("dir")
            if expected == "ltr" and actual != "ltr":
                issues.append(AuditIssue("medium", "FORM_LTR_DIR_MISSING", f"{input_type or 'text'} input should use LTR direction.", 'Set dir="ltr"; add inputmode where useful.', line, tag))
            if expected == "auto" and actual is None and input_type in {"text", "search", ""}:
                issues.append(AuditIssue("low", "FORM_AUTO_DIR_MISSING", "Free-text input has no direction hint.", 'Use dir="auto" for customer names, business names, notes, and search fields.', line, tag))
            if expected == "auto" and actual not in {"auto", None} and input_type in {"text", "search", ""}:
                issues.append(AuditIssue("low", "FORM_AUTO_DIR_RECOMMENDED", "Free-text input has a fixed direction.", 'Use dir="auto" for names, search, and free-text values.', line, tag))
            if input_type == "tel" and "inputmode" not in attrs:
                issues.append(AuditIssue("low", "FORM_TEL_INPUTMODE_MISSING", "Telephone input is missing inputmode.", 'Add inputmode="tel" for mobile keyboards.', line, tag))

        for match in TEXTAREA_RE.finditer(source):
            tag = match.group(0)
            attrs = _attrs(tag)
            if attrs.get("dir") != "auto":
                issues.append(AuditIssue("low", "TEXTAREA_AUTO_DIR_MISSING", "Textarea should accept Hebrew, Arabic, English, and mixed text.", 'Set dir="auto" on free-text textarea fields.', _line_number(source, match.start()), tag))

        mixed_patterns = (r"[A-Z]{2,}-\d", r"[\w.+-]+@[\w.-]+\.\w+", r"https?://", r"₪\s*\d", r"\d{2}/\d{2}/\d{4}")
        for pattern in mixed_patterns:
            for match in re.finditer(pattern, source):
                before = source[max(0, match.start() - 40):match.start()]
                after = source[match.end():match.end() + 40]
                context = before + match.group(0) + after
                if "<bdi" not in context.lower() and "dir=\"ltr\"" not in context.lower() and "dir='ltr'" not in context.lower():
                    issues.append(AuditIssue("low", "BIDI_DYNAMIC_VALUE_REVIEW", "Possible mixed LTR value appears without visible isolation.", "Wrap order IDs, emails, URLs, amounts, and dates with bdi or dir-specific markup.", _line_number(source, match.start()), match.group(0)))

        for class_match in CLASS_RE.finditer(source):
            result = self.audit_tailwind(class_match.group(2))
            for issue in result.issues:
                issues.append(AuditIssue(issue.severity, issue.code, issue.message, issue.recommendation, _line_number(source, class_match.start()), issue.evidence))

        return AuditResult(tuple(issues))

    async def audit_html_async(self, source: str) -> AuditResult:
        await asyncio.sleep(0)
        return self.audit_html(source)

    def audit_css(self, source: str) -> AuditResult:
        issues: list[AuditIssue] = []
        for pattern, (code, recommendation) in PHYSICAL_CSS_PATTERNS.items():
            if ":" in pattern:
                key, value = pattern.split(":", 1)
                regex = re.compile(rf"{re.escape(key)}\s*:\s*{re.escape(value.strip())}\b", re.IGNORECASE)
            else:
                regex = re.compile(rf"(?<![-\w]){re.escape(pattern)}\s*:", re.IGNORECASE)
            for match in regex.finditer(source):
                severity: Severity = "low" if code == "CSS_PHYSICAL_FLOAT" else "medium"
                issues.append(AuditIssue(severity, code, f"Physical direction CSS detected: {match.group(0).strip()}", recommendation, _line_number(source, match.start()), match.group(0).strip()))

        for match in re.finditer(r"translateX\s*\([^)]*\)", source):
            issues.append(AuditIssue("low", "CSS_TRANSLATE_X_REVIEW", "Horizontal transform may assume LTR direction.", "Review drawer, carousel, tooltip, and animation direction with RTL samples.", _line_number(source, match.start()), match.group(0)))

        for match in re.finditer(r"unicode-bidi\s*:\s*bidi-override", source, re.IGNORECASE):
            issues.append(AuditIssue("medium", "CSS_BIDI_OVERRIDE", "bidi-override forces character order and is rarely correct for UI text.", "Use bdi, dir, and unicode-bidi: isolate instead.", _line_number(source, match.start()), match.group(0)))

        return AuditResult(tuple(issues))

    async def audit_css_async(self, source: str) -> AuditResult:
        await asyncio.sleep(0)
        return self.audit_css(source)

    def audit_tailwind(self, classes: str | Sequence[str]) -> AuditResult:
        tokens = [token for token in re.split(r"\s+", classes.strip()) if token] if isinstance(classes, str) else [str(token) for token in classes]
        issues: list[AuditIssue] = []
        for token in tokens:
            base = token.split(":")[-1]
            if base in TAILWIND_EXACT:
                code, recommendation, severity = TAILWIND_EXACT[base]
                issues.append(AuditIssue(severity, code, f"Physical or reversal Tailwind utility detected: {token}", recommendation, evidence=token))
                continue
            for prefix, code, recommendation, severity in TAILWIND_PREFIXES:
                if base.startswith(prefix):
                    issues.append(AuditIssue(severity, code, f"Physical Tailwind utility detected: {token}", recommendation, evidence=token))
                    break
        return AuditResult(tuple(issues))

    async def audit_tailwind_async(self, classes: str | Sequence[str]) -> AuditResult:
        await asyncio.sleep(0)
        return self.audit_tailwind(classes)

    def audit_path(self, path: str | Path) -> AuditResult:
        file_path = Path(path)
        text = file_path.read_text(encoding="utf-8")
        suffix = file_path.suffix.lower()
        if suffix in {".html", ".htm", ".tsx", ".jsx"}:
            return self.audit_html(text)
        if suffix in {".css", ".scss"}:
            return self.audit_css(text)
        if suffix in {".txt", ".classes"}:
            return self.audit_tailwind(text)
        return AuditResult((AuditIssue("low", "UNKNOWN_FILE_TYPE", f"No specific auditor is registered for {suffix or 'files without suffix'}.", "Pass HTML, CSS, or Tailwind class text explicitly.", evidence=str(file_path)),))

    def fix_css_logical(self, source: str) -> str:
        fixed = source
        for old, new in CSS_REPLACEMENTS.items():
            fixed = re.sub(re.escape(old), new, fixed, flags=re.IGNORECASE)
        fixed = re.sub(r"(?<![-\w])left\s*:", "inset-inline-start:", fixed, flags=re.IGNORECASE)
        fixed = re.sub(r"(?<![-\w])right\s*:", "inset-inline-end:", fixed, flags=re.IGNORECASE)
        return fixed

    def create_audit(self, kind: AuditKind, source: str, *, env: Environment = "sandbox", save: bool = True) -> AuditRecord:
        if env not in {"sandbox", "production"}:
            raise ValueError("env must be 'sandbox' or 'production'")
        if kind == "html":
            result = self.audit_html(source)
        elif kind == "css":
            result = self.audit_css(source)
        elif kind == "tailwind":
            result = self.audit_tailwind(source)
        else:
            raise ValueError("kind must be 'html', 'css', or 'tailwind'")

        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        audit_id = f"audit_{stamp}_{uuid.uuid4().hex[:8]}"
        record = AuditRecord(
            id=audit_id,
            kind=kind,
            env=env,
            created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            result=result,
        )
        if save:
            self.store_dir.mkdir(parents=True, exist_ok=True)
            (self.store_dir / f"{audit_id}.json").write_text(record.to_json(), encoding="utf-8")
        return record

    async def create_audit_async(self, kind: AuditKind, source: str, *, env: Environment = "sandbox", save: bool = True) -> AuditRecord:
        await asyncio.sleep(0)
        return self.create_audit(kind, source, env=env, save=save)

    def get_audit(self, audit_id: str) -> AuditRecord:
        path = self.store_dir / f"{audit_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Audit not found: {audit_id}")
        return AuditRecord.from_dict(json.loads(path.read_text(encoding="utf-8")))

    async def get_audit_async(self, audit_id: str) -> AuditRecord:
        await asyncio.sleep(0)
        return self.get_audit(audit_id)

    def localization_profile(self, locale: str = "he-IL") -> dict[str, str]:
        direction = "rtl" if locale in {"he", "he-IL", "ar", "ar-IL"} else "ltr"
        return {
            "locale": locale,
            "dir": direction,
            "currency": "ILS",
            "currency_symbol": "₪",
            "date_policy": "DD/MM/YYYY",
            "phone_direction": "ltr",
            "id_direction": "ltr",
        }

    def production_checklist(self) -> list[str]:
        return [
            "Set lang and dir on the root layout.",
            "Derive direction from locale through one helper.",
            "Use logical CSS properties for spacing, borders, and inset.",
            "Use text-align: start for default paragraph alignment.",
            "Use bdi or dir=auto for dynamic inline values.",
            "Set email, URL, phone, ID, amount, and code fields to LTR.",
            "Use Intl.NumberFormat for ILS amounts.",
            "Use an explicit Israeli date policy such as DD/MM/YYYY.",
            "Mirror only directional icons.",
            "Avoid global flex-row-reverse or full stylesheet duplication.",
            "Test Hebrew, Arabic, English, and mixed strings.",
            "Test keyboard order and screen-reader output.",
            "Test mobile keyboards for form fields.",
            "Test generated PDFs, emails, receipts, invoices, and print views.",
            "Keep VAT and tax rates out of visual components.",
        ]

    def summarize(self, result: AuditResult) -> str:
        summary = result.summary
        return f"{summary['total']} issue(s): {summary['high']} high, {summary['medium']} medium, {summary['low']} low."


__all__ = [
    "AuditIssue",
    "AuditKind",
    "AuditRecord",
    "AuditResult",
    "Direction",
    "Environment",
    "RtlAuditClient",
    "format_dd_mm_yyyy",
    "infer_direction",
    "merge_results",
    "recommend_input_attributes",
    "recommended_input_dir",
    "validate_israeli_id",
]
