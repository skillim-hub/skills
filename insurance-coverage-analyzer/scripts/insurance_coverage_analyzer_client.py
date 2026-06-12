"""Typed local client for Israeli insurance coverage analysis.

No network calls are made. The client accepts structured policy records, normalizes
values, compares policy-level terms, flags duplicates and gaps, and returns
deterministic reports for CLI usage and tests.
"""

from __future__ import annotations

import asyncio
import csv
import json
import math
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Mapping, Optional, Sequence, Tuple, Union

__version__ = "2.1.0"

PolicyType = Literal["health", "home", "life", "unknown"]
Severity = Literal["low", "medium", "high", "critical"]


class PolicyValidationError(ValueError):
    """Raised when policy input cannot be safely validated."""


SENSITIVE_ID_RE = re.compile(r"\b\d{9}\b")
MONEY_RE = re.compile(r"(?P<num>\d+(?:,\d{3})*(?:\.\d+)?)\s*(?:₪|ש\"ח|nis|NIS)?")
DATE_FORMATS = ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d")

TYPE_ALIASES: Dict[str, PolicyType] = {
    "health": "health", "medical": "health", "private medical": "health",
    "ביטוח בריאות": "health", "בריאות": "health",
    "home": "home", "apartment": "home", "contents": "home", "structure": "home",
    "ביטוח דירה": "home", "דירה": "home", "מבנה": "home", "תכולה": "home",
    "life": "life", "term": "life", "risk": "life", "mortgage life": "life",
    "ביטוח חיים": "life", "חיים": "life", "ריסק": "life",
}

ESSENTIAL_COVERAGES: Dict[PolicyType, Tuple[str, ...]] = {
    "health": ("private_surgery_israel", "drugs_outside_basket", "transplants", "ambulatory"),
    "home": ("structure", "contents", "water_damage", "earthquake", "third_party_liability"),
    "life": ("death_benefit", "beneficiaries"),
    "unknown": (),
}

DUPLICATE_GROUPS: Tuple[Tuple[str, ...], ...] = (
    ("serious_illness", "critical_illness"),
    ("private_surgery_israel", "supplementary_surgery"),
    ("death_benefit", "mortgage_life"),
    ("contents", "business_equipment"),
)


@dataclass(frozen=True)
class CoverageItem:
    covered: Optional[bool] = None
    limit_nis: Optional[float] = None
    deductible_nis: Optional[float] = None
    deductible_percent: Optional[float] = None
    waiting_period_days: Optional[int] = None
    notes: str = ""

    @classmethod
    def from_raw(cls, raw: Any) -> "CoverageItem":
        if isinstance(raw, CoverageItem):
            return raw
        if isinstance(raw, bool):
            return cls(covered=raw)
        if isinstance(raw, (int, float)):
            return cls(covered=True, limit_nis=float(raw))
        if raw is None:
            return cls()
        if isinstance(raw, str):
            lowered = raw.strip().lower()
            amount = parse_money(raw)
            if lowered in {"yes", "true", "covered", "כן", "מכוסה"}:
                return cls(covered=True, notes=raw)
            if lowered in {"no", "false", "not covered", "לא", "לא מכוסה"}:
                return cls(covered=False, notes=raw)
            return cls(covered=True if amount is not None else None, limit_nis=amount, notes=raw)
        if isinstance(raw, Mapping):
            return cls(
                covered=to_bool(raw.get("covered")),
                limit_nis=to_float(raw.get("limit_nis", raw.get("limit"))),
                deductible_nis=to_float(raw.get("deductible_nis", raw.get("deductible"))),
                deductible_percent=to_float(raw.get("deductible_percent")),
                waiting_period_days=to_int(raw.get("waiting_period_days")),
                notes=str(raw.get("notes", "")),
            )
        raise TypeError(f"Unsupported coverage item type: {type(raw)!r}")

    def exposure_nis(self, basis_nis: Optional[float]) -> Optional[float]:
        if self.deductible_nis is not None:
            return self.deductible_nis
        if self.deductible_percent is not None and basis_nis is not None:
            return round(basis_nis * self.deductible_percent / 100.0, 2)
        return None

    def to_display(self) -> str:
        parts: List[str] = []
        parts.append("covered" if self.covered is True else "not covered" if self.covered is False else "unknown")
        if self.limit_nis is not None:
            parts.append(f"limit {format_nis(self.limit_nis)}")
        if self.deductible_nis is not None:
            parts.append(f"deductible {format_nis(self.deductible_nis)}")
        if self.deductible_percent is not None:
            parts.append(f"deductible {self.deductible_percent:g}%")
        if self.waiting_period_days is not None:
            parts.append(f"waiting {self.waiting_period_days} days")
        if self.notes:
            parts.append(self.notes)
        return ", ".join(parts)


@dataclass
class Policy:
    policy_id: str
    policy_type: PolicyType
    insurer: str = "Unknown insurer"
    policy_name: str = "Unnamed policy"
    policy_number: Optional[str] = None
    holder_type: Optional[str] = None
    start_date: Optional[str] = None
    renewal_date: Optional[str] = None
    premium_monthly_nis: Optional[float] = None
    premium_annual_nis: Optional[float] = None
    coverages: Dict[str, CoverageItem] = field(default_factory=dict)
    exclusions: List[str] = field(default_factory=list)
    waiting_period_days: Optional[int] = None
    index_linkage: Optional[str] = None
    source: Dict[str, Any] = field(default_factory=dict)
    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_raw(cls, raw: Mapping[str, Any], index: int = 0) -> "Policy":
        if not isinstance(raw, Mapping):
            raise PolicyValidationError("Policy must be an object")
        policy_id = str(raw.get("policy_id") or raw.get("id") or f"policy-{index + 1}")
        policy_type = normalize_policy_type(raw.get("policy_type") or raw.get("type") or "")
        monthly = to_float(raw.get("premium_monthly_nis", raw.get("premium_monthly")))
        annual = to_float(raw.get("premium_annual_nis", raw.get("premium_annual")))
        if monthly is None and annual is not None:
            monthly = round(annual / 12.0, 2)
        if annual is None and monthly is not None:
            annual = round(monthly * 12.0, 2)
        cov_raw = raw.get("coverages") or {}
        if not isinstance(cov_raw, Mapping):
            raise PolicyValidationError(f"{policy_id}: coverages must be an object")
        exclusions_raw = raw.get("exclusions") or []
        exclusions = [exclusions_raw] if isinstance(exclusions_raw, str) else [str(x) for x in exclusions_raw]
        return cls(
            policy_id=policy_id,
            policy_type=policy_type,
            insurer=str(raw.get("insurer") or raw.get("company") or "Unknown insurer"),
            policy_name=str(raw.get("policy_name") or raw.get("name") or "Unnamed policy"),
            policy_number=redact_sensitive_text(str(raw.get("policy_number"))) if raw.get("policy_number") else None,
            holder_type=str(raw.get("holder_type")) if raw.get("holder_type") else None,
            start_date=normalize_date(raw.get("start_date")),
            renewal_date=normalize_date(raw.get("renewal_date")),
            premium_monthly_nis=monthly,
            premium_annual_nis=annual,
            coverages={str(k): CoverageItem.from_raw(v) for k, v in cov_raw.items()},
            exclusions=exclusions,
            waiting_period_days=to_int(raw.get("waiting_period_days")),
            index_linkage=str(raw.get("index_linkage")) if raw.get("index_linkage") else None,
            source=dict(raw.get("source") or {}),
            raw=dict(raw),
        )

    def validate(self) -> List[str]:
        warnings: List[str] = []
        if self.policy_type == "unknown":
            warnings.append("INVALID_POLICY_TYPE")
        if self.premium_monthly_nis is None and self.premium_annual_nis is None:
            warnings.append("MISSING_PREMIUM")
        if not self.coverages:
            warnings.append("MISSING_COVERAGE_MAP")
        if has_sensitive_identifier(json.dumps(self.raw, ensure_ascii=False)):
            warnings.append("SENSITIVE_IDENTIFIER")
        if self.raw.get("renewal_date") and self.renewal_date is None:
            warnings.append("DATE_AMBIGUOUS")
        return warnings

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["coverages"] = {k: asdict(v) for k, v in self.coverages.items()}
        return data


@dataclass
class DiffItem:
    category: str
    policy_a: str
    policy_b: str
    practical_effect: str
    severity: Severity = "low"

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class ComparisonResult:
    summary: str
    policies: List[Dict[str, Any]]
    diffs: List[DiffItem]
    duplicates: List[str]
    gaps: List[str]
    risk_flags: List[str]
    actions: List[str]
    scorecard: Dict[str, int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "policies": self.policies,
            "diffs": [d.to_dict() for d in self.diffs],
            "duplicates": self.duplicates,
            "gaps": self.gaps,
            "risk_flags": self.risk_flags,
            "actions": self.actions,
            "scorecard": self.scorecard,
        }

    def to_markdown(self, locale: str = "en-IL") -> str:
        he = locale.lower().startswith("he")
        headings = {
            "summary": "## תקציר" if he else "## Summary",
            "diff": "## השוואה ברמת הפוליסה" if he else "## Policy-level diff",
            "dups": "## כפילויות ופערים" if he else "## Duplicates and gaps",
            "risks": "## דגלי סיכון" if he else "## Risk flags",
            "actions": "## פעולות" if he else "## Actions",
        }
        lines = [headings["summary"], self.summary, "", headings["diff"]]
        lines.append("| Category | Policy A | Policy B | Practical effect | Severity |")
        lines.append("|---|---|---|---|---|")
        for diff in self.diffs:
            lines.append(f"| {diff.category} | {diff.policy_a} | {diff.policy_b} | {diff.practical_effect} | {diff.severity} |")
        lines.extend(["", headings["dups"]])
        for item in self.duplicates or ["None found"]:
            lines.append(f"- {item}")
        for item in self.gaps:
            lines.append(f"- Gap: {item}")
        lines.extend(["", headings["risks"]])
        for item in self.risk_flags or ["None found"]:
            lines.append(f"- {item}")
        lines.extend(["", headings["actions"]])
        for item in self.actions:
            lines.append(f"- {item}")
        return "\n".join(lines)


class InsuranceCoverageAnalyzer:
    """Local sync and async analyzer."""

    def __init__(self, locale: str = "en-IL") -> None:
        self.locale = locale

    def normalize(self, raw_policies: Sequence[Mapping[str, Any]]) -> List[Policy]:
        policies = [Policy.from_raw(raw, i) for i, raw in enumerate(raw_policies)]
        ids = [p.policy_id for p in policies]
        if len(ids) != len(set(ids)):
            raise PolicyValidationError("Duplicate policy_id values are not allowed")
        return policies

    async def normalize_async(self, raw_policies: Sequence[Mapping[str, Any]]) -> List[Policy]:
        await asyncio.sleep(0)
        return self.normalize(raw_policies)

    def validate(self, raw_policies: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        policies = self.normalize(raw_policies)
        warnings = {p.policy_id: p.validate() for p in policies}
        return {"valid": not any("INVALID_POLICY_TYPE" in w for w in warnings.values()), "warnings": warnings, "policy_count": len(policies)}

    async def validate_async(self, raw_policies: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return self.validate(raw_policies)

    def compare(self, raw_policies: Sequence[Mapping[str, Any]], profile: Optional[Mapping[str, Any]] = None) -> ComparisonResult:
        policies = self.normalize(raw_policies)
        if not policies:
            raise PolicyValidationError("At least one policy is required")
        profile = profile or {}
        diffs = compare_policy_set(policies)
        duplicates = detect_duplicates(policies)
        gaps = detect_gaps(policies, profile)
        risk_flags = detect_risk_flags(policies, profile)
        actions = recommend_actions(policies, diffs, duplicates, gaps, risk_flags)
        scorecard = score_policies(policies)
        summary = build_summary(diffs, gaps, risk_flags, self.locale)
        return ComparisonResult(summary, [p.to_dict() for p in policies], diffs, duplicates, gaps, risk_flags, actions, scorecard)

    async def compare_async(self, raw_policies: Sequence[Mapping[str, Any]], profile: Optional[Mapping[str, Any]] = None) -> ComparisonResult:
        await asyncio.sleep(0)
        return self.compare(raw_policies, profile)

    def load_json(self, path: Union[str, Path]) -> Tuple[List[Mapping[str, Any]], Dict[str, Any]]:
        return load_policy_json(path)

    def load_csv(self, path: Union[str, Path]) -> List[Mapping[str, Any]]:
        return load_policy_csv(path)


def normalize_policy_type(value: Any) -> PolicyType:
    return TYPE_ALIASES.get(str(value or "").strip().lower(), "unknown")


def normalize_date(value: Any) -> Optional[str]:
    if value in (None, ""):
        return None
    text = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).strftime("%d-%m-%Y")
        except ValueError:
            pass
    return None


def parse_money(value: Any) -> Optional[float]:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = MONEY_RE.search(str(value))
    if not match:
        return None
    return float(match.group("num").replace(",", ""))


def format_nis(value: Optional[float]) -> str:
    if value is None:
        return "unknown"
    return f"₪{int(round(value)):,}" if math.isclose(value, round(value)) else f"₪{value:,.2f}"


def has_sensitive_identifier(text: str) -> bool:
    return bool(SENSITIVE_ID_RE.search(text))


def redact_sensitive_text(text: str) -> str:
    return SENSITIVE_ID_RE.sub("***REDACTED-ID***", text)


def to_bool(value: Any) -> Optional[bool]:
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "yes", "y", "1", "covered", "כן", "מכוסה"}:
        return True
    if text in {"false", "no", "n", "0", "not covered", "לא", "לא מכוסה"}:
        return False
    return None


def to_float(value: Any) -> Optional[float]:
    return parse_money(value)


def to_int(value: Any) -> Optional[int]:
    if value in (None, ""):
        return None
    try:
        return int(float(str(value).replace(",", "")))
    except (TypeError, ValueError):
        return None


def load_policy_json(path: Union[str, Path]) -> Tuple[List[Mapping[str, Any]], Dict[str, Any]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data, {}
    if isinstance(data, Mapping) and isinstance(data.get("policies"), list):
        return data["policies"], dict(data.get("profile") or {})
    raise PolicyValidationError("JSON must be a list or an object with policies")


def load_policy_csv(path: Union[str, Path]) -> List[Mapping[str, Any]]:
    rows: List[Mapping[str, Any]] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            coverage_key = row.get("coverage_key")
            coverages: Dict[str, Any] = {}
            if coverage_key:
                coverages[coverage_key] = {
                    "covered": to_bool(row.get("covered")),
                    "limit_nis": to_float(row.get("limit_nis")),
                    "deductible_nis": to_float(row.get("deductible_nis")),
                    "deductible_percent": to_float(row.get("deductible_percent")),
                }
            rows.append({
                "policy_id": row.get("policy_id"),
                "policy_type": row.get("policy_type"),
                "insurer": row.get("insurer"),
                "policy_name": row.get("policy_name"),
                "premium_monthly_nis": to_float(row.get("premium_monthly_nis")),
                "premium_annual_nis": to_float(row.get("premium_annual_nis")),
                "coverages": coverages,
            })
    return rows


def compare_policy_set(policies: Sequence[Policy]) -> List[DiffItem]:
    if len(policies) == 1:
        return [DiffItem(m, "not found", "not applicable", f"Essential {policies[0].policy_type} coverage is missing or unknown.", "high") for m in missing_essential_coverages(policies[0])]
    a, b = policies[0], policies[1]
    diffs: List[DiffItem] = []
    if a.policy_type != b.policy_type:
        diffs.append(DiffItem("policy_type", a.policy_type, b.policy_type, "Policies are different types; direct ranking is not reliable.", "high"))
    if a.premium_annual_nis is not None and b.premium_annual_nis is not None and not math.isclose(a.premium_annual_nis, b.premium_annual_nis):
        delta = b.premium_annual_nis - a.premium_annual_nis
        cheaper = a.policy_id if delta > 0 else b.policy_id
        diffs.append(DiffItem("annual_premium", format_nis(a.premium_annual_nis), format_nis(b.premium_annual_nis), f"{cheaper} is cheaper by {format_nis(abs(delta))} per year.", "medium"))
    for key in sorted(set(a.coverages) | set(b.coverages)):
        item_a = a.coverages.get(key, CoverageItem())
        item_b = b.coverages.get(key, CoverageItem())
        if item_a != item_b:
            diffs.append(compare_coverage_item(key, item_a, item_b, a, b))
    if set(a.exclusions) != set(b.exclusions):
        severity: Severity = "high" if a.policy_type in {"health", "life"} else "medium"
        diffs.append(DiffItem("exclusions", ", ".join(a.exclusions) or "none listed", ", ".join(b.exclusions) or "none listed", "Different exclusions can materially change claim approval.", severity))
    if a.waiting_period_days != b.waiting_period_days:
        diffs.append(DiffItem("waiting_period", days(a.waiting_period_days), days(b.waiting_period_days), "Shorter waiting period improves near-term usability.", "medium"))
    return diffs


def compare_coverage_item(key: str, a: CoverageItem, b: CoverageItem, policy_a: Policy, policy_b: Policy) -> DiffItem:
    severity: Severity = "low"
    effects: List[str] = []
    if a.covered != b.covered:
        severity = "high"
        effects.append("Coverage presence differs.")
    if a.limit_nis != b.limit_nis:
        severity = max_severity(severity, "medium")
        if a.limit_nis is not None and b.limit_nis is not None:
            higher = policy_a.policy_id if a.limit_nis > b.limit_nis else policy_b.policy_id
            effects.append(f"{higher} has the higher limit.")
        else:
            effects.append("One policy lacks a listed limit.")
    exp_a, exp_b = a.exposure_nis(coverage_basis(policy_a)), b.exposure_nis(coverage_basis(policy_b))
    if exp_a != exp_b:
        severity = max_severity(severity, "medium")
        effects.append("Deductible exposure differs or is unknown.")
    if a.waiting_period_days != b.waiting_period_days:
        severity = max_severity(severity, "medium")
        effects.append("Waiting period differs.")
    return DiffItem(key, a.to_display(), b.to_display(), " ".join(effects) or "Terms differ.", severity)


def missing_essential_coverages(policy: Policy) -> List[str]:
    return [k for k in ESSENTIAL_COVERAGES.get(policy.policy_type, ()) if k not in policy.coverages]


def detect_duplicates(policies: Sequence[Policy]) -> List[str]:
    presence: Dict[str, List[str]] = {}
    for policy in policies:
        for key, item in policy.coverages.items():
            if item.covered is not False:
                presence.setdefault(key, []).append(policy.policy_id)
    duplicates = [f"{key} appears in multiple policies: {', '.join(ids)}" for key, ids in presence.items() if len(ids) > 1]
    keys = set(presence)
    for group in DUPLICATE_GROUPS:
        matched = [key for key in group if key in keys]
        if len(matched) > 1:
            duplicates.append(f"Potential overlap across related coverages: {', '.join(matched)}")
    return sorted(set(duplicates))


def detect_gaps(policies: Sequence[Policy], profile: Optional[Mapping[str, Any]] = None) -> List[str]:
    profile = profile or {}
    gaps: List[str] = []
    for policy in policies:
        for missing in missing_essential_coverages(policy):
            gaps.append(f"{policy.policy_id}: {missing} not found")
        if policy.policy_type == "home":
            if profile.get("mortgage") and "structure" not in policy.coverages:
                gaps.append(f"{policy.policy_id}: mortgage profile but structure cover not found")
            if profile.get("domestic_worker") and "employer_liability" not in policy.coverages:
                gaps.append(f"{policy.policy_id}: employer liability not found")
            if profile.get("home_office") and "business_equipment" not in policy.coverages:
                gaps.append(f"{policy.policy_id}: business equipment cover not found")
            eq = policy.coverages.get("earthquake")
            if eq:
                exposure = eq.exposure_nis(coverage_basis(policy))
                if exposure and exposure >= 50000:
                    gaps.append(f"{policy.policy_id}: earthquake deductible exposure is {format_nis(exposure)}")
        if policy.policy_type == "life":
            if "mortgage_life" in policy.coverages and "death_benefit" not in policy.coverages:
                gaps.append(f"{policy.policy_id}: mortgage life found; family death benefit not separately found")
            if "beneficiaries" not in policy.coverages and not policy.raw.get("beneficiaries"):
                gaps.append(f"{policy.policy_id}: beneficiary wording not found")
        if policy.policy_type == "health":
            if policy.waiting_period_days and policy.waiting_period_days > 90:
                gaps.append(f"{policy.policy_id}: waiting period exceeds configured 90-day review threshold")
            if policy.exclusions:
                gaps.append(f"{policy.policy_id}: exclusions require condition-specific review")
    return sorted(set(gaps))


def detect_risk_flags(policies: Sequence[Policy], profile: Optional[Mapping[str, Any]] = None) -> List[str]:
    profile = profile or {}
    flags: List[str] = []
    if len({p.policy_type for p in policies}) > 1:
        flags.append("Mixed policy types supplied; avoid direct price ranking.")
    for policy in policies:
        if policy.policy_type in {"health", "life"} and (policy.exclusions or policy.raw.get("requires_underwriting") or policy.raw.get("known_condition")):
            flags.append(f"{policy.policy_id}: request licensed review before cancellation or replacement.")
        if policy.policy_type == "life" and ("mortgage_life" in policy.coverages or policy.raw.get("assigned_to_bank")):
            flags.append(f"{policy.policy_id}: mortgage assignment may pay the bank before family.")
        if policy.policy_type == "home" and profile.get("mortgage"):
            flags.append(f"{policy.policy_id}: confirm mortgage lender clause before switching.")
        if policy.index_linkage:
            flags.append(f"{policy.policy_id}: index linkage affects long-term cost and benefit.")
        if policy.raw.get("first_year_discount"):
            flags.append(f"{policy.policy_id}: first-year discount may hide renewal cost.")
    return sorted(set(flags))


def recommend_actions(policies: Sequence[Policy], diffs: Sequence[DiffItem], duplicates: Sequence[str], gaps: Sequence[str], risk_flags: Sequence[str]) -> List[str]:
    actions: List[str] = []
    if any(d.severity in {"high", "critical"} for d in diffs):
        actions.append("Request full policy wording for all high-severity differences.")
    if duplicates:
        actions.append("Clarify whether duplicated coverages add practical value before reducing cover.")
    if gaps:
        actions.append("Ask the insurer or licensed agent to confirm each listed gap in writing.")
    if risk_flags:
        actions.append("Request licensed review before cancellation or replacement.")
    if any(p.premium_annual_nis is not None for p in policies):
        actions.append("Use annual ₪ cost when negotiating renewal.")
    return actions or ["Document the comparison and keep coverage under review."]


def score_policies(policies: Sequence[Policy]) -> Dict[str, int]:
    scores: Dict[str, int] = {}
    for policy in policies:
        score = min(30, sum(1 for item in policy.coverages.values() if item.covered is not False) * 5)
        score += 25 if not policy.exclusions else max(5, 25 - len(policy.exclusions) * 5)
        score += 20 if policy.premium_annual_nis is not None else 0
        score += 15 if not missing_essential_coverages(policy) else 0
        score += 5 if policy.renewal_date or policy.index_linkage else 0
        score += 5 if policy.raw.get("cancellation_notice_days") is not None else 0
        scores[policy.policy_id] = min(100, score)
    return scores


def build_summary(diffs: Sequence[DiffItem], gaps: Sequence[str], risk_flags: Sequence[str], locale: str = "en-IL") -> str:
    he = locale.lower().startswith("he")
    if he:
        if risk_flags:
            return "נמצא סיכון מהותי. בדוק את דגלי הסיכון לפני ביטול או החלפה."
        if gaps:
            return "נמצאו פערי כיסוי שיש לברר לפני החלטה."
        return "ההשוואה הושלמה. בדוק את ההבדלים והפעולות המומלצות."
    if risk_flags:
        return "Material risk was found. Review risk flags before cancellation or replacement."
    if gaps:
        return "Coverage gaps were found. Clarify them before deciding."
    if diffs:
        return "Policy differences were found. Review the diff and prioritize high-severity items."
    return "No material differences were found from the supplied structured data."


def save_report(result: ComparisonResult, path: Union[str, Path], format: str = "json") -> None:
    target = Path(path)
    if format == "json":
        target.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    elif format == "markdown":
        target.write_text(result.to_markdown(), encoding="utf-8")
    else:
        raise ValueError("format must be json or markdown")


def sample_policies() -> List[Dict[str, Any]]:
    return [
        {
            "policy_id": "health-a",
            "policy_type": "health",
            "insurer": "Insurer A",
            "policy_name": "Private Health Plus",
            "premium_monthly_nis": 180,
            "coverages": {
                "private_surgery_israel": {"covered": True, "limit_nis": 1000000, "deductible_nis": 0},
                "drugs_outside_basket": {"covered": True, "limit_nis": 2000000},
                "ambulatory": {"covered": True, "limit_nis": 6000},
            },
            "exclusions": ["left knee condition"],
            "waiting_period_days": 90,
        },
        {
            "policy_id": "health-b",
            "policy_type": "health",
            "insurer": "Insurer B",
            "policy_name": "Medical Shield",
            "premium_monthly_nis": 145,
            "coverages": {
                "private_surgery_israel": {"covered": True, "limit_nis": 750000, "deductible_nis": 500},
                "drugs_outside_basket": {"covered": True, "limit_nis": 1500000},
            },
            "waiting_period_days": 120,
        },
    ]


def coverage_basis(policy: Policy) -> Optional[float]:
    for key in ("structure", "contents", "death_benefit"):
        item = policy.coverages.get(key)
        if item and item.limit_nis is not None:
            return item.limit_nis
    limits = [item.limit_nis for item in policy.coverages.values() if item.limit_nis is not None]
    return max(limits) if limits else None


def days(value: Optional[int]) -> str:
    return "unknown" if value is None else f"{value} days"


def max_severity(a: Severity, b: Severity) -> Severity:
    order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    return a if order[a] >= order[b] else b


def format_date_for_locale(value: Any, locale: str = "en-IL") -> Optional[str]:
    """Return a normalized date with Hebrew display using DD/MM/YYYY."""
    normalized = normalize_date(value)
    if normalized is None:
        return None
    if locale.lower().startswith("he"):
        return normalized.replace("-", "/")
    return normalized


def create_analysis_record(
    raw_policies: Sequence[Mapping[str, Any]],
    profile: Optional[Mapping[str, Any]] = None,
    store_dir: Union[str, Path] = ".ica_runs",
    locale: str = "en-IL",
) -> Dict[str, Any]:
    """Create a persisted comparison record and return its identifier."""
    import hashlib
    import time

    analyzer = InsuranceCoverageAnalyzer(locale=locale)
    result = analyzer.compare(raw_policies, profile=profile)
    payload = {
        "policies": list(raw_policies),
        "profile": dict(profile or {}),
        "result": result.to_dict(),
        "created_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "locale": locale,
    }
    digest_source = json.dumps(payload, ensure_ascii=False, sort_keys=True) + str(time.time_ns())
    analysis_id = "ica-" + hashlib.sha256(digest_source.encode("utf-8")).hexdigest()[:12]
    payload["analysis_id"] = analysis_id
    target_dir = Path(store_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / f"{analysis_id}.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return {"analysis_id": analysis_id, "path": str(target_dir / f"{analysis_id}.json"), "summary": result.summary}


def load_analysis_record(analysis_id: str, store_dir: Union[str, Path] = ".ica_runs") -> Dict[str, Any]:
    """Load a persisted comparison record by identifier."""
    safe_id = re.sub(r"[^A-Za-z0-9_.-]", "", analysis_id)
    path = Path(store_dir) / f"{safe_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"analysis record not found: {analysis_id}")
    return json.loads(path.read_text(encoding="utf-8"))


__all__ = [
    "CoverageItem", "Policy", "DiffItem", "ComparisonResult", "InsuranceCoverageAnalyzer",
    "PolicyValidationError", "normalize_policy_type", "normalize_date", "parse_money",
    "format_nis", "has_sensitive_identifier", "redact_sensitive_text", "load_policy_json",
    "load_policy_csv", "compare_policy_set", "detect_duplicates", "detect_gaps",
    "detect_risk_flags", "recommend_actions", "score_policies", "save_report",
    "sample_policies", "format_date_for_locale", "create_analysis_record", "load_analysis_record",
]
