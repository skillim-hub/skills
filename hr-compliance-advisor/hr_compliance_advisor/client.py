"""Offline helper for Israeli HR compliance triage.

The module performs deterministic checks for common small-business and worker
scenarios. It does not fetch current legal rates. Override ComplianceConfig
after checking official Israeli sources for the relevant period.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import uuid
from dataclasses import asdict, dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Mapping, Optional, Sequence

WorkerType = Literal["employee", "contractor", "candidate", "unknown"]
RiskName = Literal["low", "medium", "high", "critical"]


class RiskLevel(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

    @property
    def label(self) -> RiskName:
        return {1: "low", 2: "medium", 3: "high", 4: "critical"}[int(self)]


@dataclass(frozen=True)
class ComplianceConfig:
    """Configurable thresholds. Defaults are examples; verify before use."""

    minimum_monthly_wage_ils: float = 6443.85
    minimum_hourly_wage_ils: float = 35.40
    regular_weekly_hours: float = 42.0
    regular_daily_hours: float = 8.6
    max_daily_hours_including_overtime: float = 12.0
    max_weekly_overtime_hours: float = 16.0
    pension_waiting_months_without_prior_plan: int = 6
    pension_waiting_months_with_prior_plan: int = 3
    employer_pension_min_pct: float = 6.5
    severance_deposit_min_pct: float = 6.0
    section_14_full_severance_pct: float = 8.33
    source_note: str = "Defaults reflect web-verified general adult minimum wage as of 04/06/2026; verify pay-period and sector rules before action."


@dataclass(frozen=True)
class EmployeeFacts:
    worker_type: WorkerType = "unknown"
    sector: str = "general"
    monthly_salary_ils: Optional[float] = None
    hourly_rate_ils: Optional[float] = None
    weekly_hours: Optional[float] = None
    daily_hours: Optional[float] = None
    overtime_hours_weekly: float = 0.0
    tenure_months: float = 0.0
    part_time_ratio: float = 1.0
    had_active_pension_before_start: Optional[bool] = None
    has_pension_arrangement: Optional[bool] = None
    pension_start_month: Optional[int] = None
    has_section_14: Optional[bool] = None
    employer_contribution_pension_pct: Optional[float] = None
    employer_contribution_severance_pct: Optional[float] = None
    is_parent_or_pregnant: bool = False
    is_on_reserve_duty_or_recently_returned: bool = False
    termination_reason: Optional[str] = None
    notice_days_given: Optional[int] = None
    contractor_controls: int = 0
    contract_text: str = ""
    notes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ComplianceFinding:
    code: str
    title: str
    risk: RiskLevel
    explanation: str
    recommendation: str
    law_refs: Sequence[str]
    evidence: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["risk"] = self.risk.label
        return data


class InputValidationError(ValueError):
    """Raised when review input cannot be processed safely."""


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip()).lower()


def _contains_any(text: str, patterns: Iterable[str]) -> bool:
    normalized = _norm(text)
    return any(re.search(pattern, normalized, flags=re.IGNORECASE) for pattern in patterns)


ENVIRONMENT = Literal["sandbox", "production"]


def config_from_env(environ: Optional[Mapping[str, str]] = None, base: Optional[ComplianceConfig] = None) -> ComplianceConfig:
    """Build configuration from environment variables.

    Supported variables:
    HR_COMPLIANCE_MIN_MONTHLY_WAGE_ILS, HR_COMPLIANCE_MIN_HOURLY_WAGE_ILS,
    HR_COMPLIANCE_REGULAR_WEEKLY_HOURS, HR_COMPLIANCE_REGULAR_DAILY_HOURS,
    HR_COMPLIANCE_MAX_DAILY_HOURS, HR_COMPLIANCE_MAX_WEEKLY_OVERTIME_HOURS.
    """

    source = dict(os.environ if environ is None else environ)
    values = asdict(base or ComplianceConfig())
    mapping = {
        "HR_COMPLIANCE_MIN_MONTHLY_WAGE_ILS": "minimum_monthly_wage_ils",
        "HR_COMPLIANCE_MIN_HOURLY_WAGE_ILS": "minimum_hourly_wage_ils",
        "HR_COMPLIANCE_REGULAR_WEEKLY_HOURS": "regular_weekly_hours",
        "HR_COMPLIANCE_REGULAR_DAILY_HOURS": "regular_daily_hours",
        "HR_COMPLIANCE_MAX_DAILY_HOURS": "max_daily_hours_including_overtime",
        "HR_COMPLIANCE_MAX_WEEKLY_OVERTIME_HOURS": "max_weekly_overtime_hours",
    }
    for env_name, field_name in mapping.items():
        raw = source.get(env_name)
        if raw not in (None, ""):
            values[field_name] = float(raw)
    if any(name in source for name in mapping):
        values["source_note"] = "Configured from environment variables; verify values against official Israeli sources."
    return ComplianceConfig(**values)


def _case_path(case_dir: str | Path, case_id: str) -> Path:
    safe = re.sub(r"[^a-zA-Z0-9_-]", "", case_id)
    if not safe:
        raise InputValidationError("INVALID_CASE_ID")
    return Path(case_dir) / f"{safe}.json"


def validate_facts(facts: EmployeeFacts) -> None:
    if facts.worker_type not in {"employee", "contractor", "candidate", "unknown"}:
        raise InputValidationError("INVALID_WORKER_TYPE")
    if any(v is not None and v < 0 for v in [facts.monthly_salary_ils, facts.hourly_rate_ils]):
        raise InputValidationError("NEGATIVE_AMOUNT")
    if any(v is not None and v < 0 for v in [facts.weekly_hours, facts.daily_hours, facts.overtime_hours_weekly]):
        raise InputValidationError("HOURS_OUT_OF_RANGE")
    if facts.weekly_hours is not None and facts.weekly_hours > 120:
        raise InputValidationError("HOURS_OUT_OF_RANGE")
    if facts.daily_hours is not None and facts.daily_hours > 24:
        raise InputValidationError("HOURS_OUT_OF_RANGE")
    if facts.tenure_months < 0:
        raise InputValidationError("MISSING_TENURE")
    if not 0 < facts.part_time_ratio <= 1.5:
        raise InputValidationError("HOURS_OUT_OF_RANGE")


def required_notice_days(tenure_months: float, monthly_employee: bool = True) -> int:
    if tenure_months <= 0:
        return 0
    if monthly_employee:
        if tenure_months <= 6:
            return int(tenure_months)
        if tenure_months < 12:
            return int(round(6 + (tenure_months - 6) * 2.5))
        return 30
    if tenure_months < 12:
        return int(tenure_months)
    if tenure_months < 24:
        return int(round(14 + (tenure_months - 12) / 2))
    if tenure_months < 36:
        return int(round(21 + (tenure_months - 24) / 2))
    return 30


def f(code: str, title: str, risk: RiskLevel, explanation: str, recommendation: str, refs: Sequence[str], evidence: Mapping[str, Any] | None = None) -> ComplianceFinding:
    return ComplianceFinding(code, title, risk, explanation, recommendation, refs, evidence or {})


def review_minimum_wage(facts: EmployeeFacts, config: ComplianceConfig) -> List[ComplianceFinding]:
    out: List[ComplianceFinding] = []
    if facts.worker_type not in {"employee", "unknown"}:
        return out
    if facts.hourly_rate_ils is not None and facts.hourly_rate_ils < config.minimum_hourly_wage_ils:
        out.append(f("MIN_WAGE_HOURLY", "Hourly rate may be below Israeli minimum wage", RiskLevel.CRITICAL,
                     "The stated hourly rate is below the configured minimum wage benchmark.",
                     "Verify the official hourly minimum for the pay period, raise the rate, and calculate arrears.",
                     ["Minimum Wage Law, 5747-1987"], {"hourly_rate_ils": facts.hourly_rate_ils, "configured_min_hourly_ils": config.minimum_hourly_wage_ils}))
    if facts.monthly_salary_ils is not None:
        required = config.minimum_monthly_wage_ils * min(max(facts.part_time_ratio, 0), 1.0)
        if facts.monthly_salary_ils < required:
            out.append(f("MIN_WAGE_MONTHLY", "Monthly salary may be below Israeli minimum wage", RiskLevel.CRITICAL,
                         "The stated monthly salary is below the configured monthly minimum benchmark after part-time adjustment.",
                         "Verify the official monthly minimum for the pay period and adjust salary or scope.",
                         ["Minimum Wage Law, 5747-1987"], {"monthly_salary_ils": facts.monthly_salary_ils, "required_monthly_ils": round(required, 2)}))
    if facts.worker_type == "employee" and facts.monthly_salary_ils is None and facts.hourly_rate_ils is None:
        out.append(f("MISSING_WAGE_BASIS", "Wage basis is missing", RiskLevel.MEDIUM,
                     "Minimum wage compliance cannot be tested without a wage amount.",
                     "Add monthly salary, hourly rate, daily rate, or piecework data.",
                     ["Minimum Wage Law, 5747-1987"]))
    text = facts.contract_text
    if _contains_any(text, [r"unpaid training", r"training.*unpaid", r"הכשרה.*ללא תשלום"]):
        out.append(f("UNPAID_TRAINING_TIME", "Mandatory training may be unpaid work time", RiskLevel.HIGH,
                     "The text suggests training time may be excluded from paid working time.",
                     "Treat mandatory training as compensable time unless a verified exception applies.",
                     ["Minimum Wage Law, 5747-1987", "Protection of Wages Law, 5718-1958"], {"text_match": "unpaid training"}))
    if _contains_any(text, [r"closing time.*unpaid", r"unpaid closing", r"סגיר.*ללא תשלום"]):
        out.append(f("UNPAID_CLOSING_TIME", "Closing or setup time may be unpaid work time", RiskLevel.HIGH,
                     "The text suggests required setup or closing work may be unpaid.",
                     "Include opening, closing, cash-up, and setup time in paid work time.",
                     ["Minimum Wage Law, 5747-1987", "Protection of Wages Law, 5718-1958"], {"text_match": "unpaid closing time"}))
    return out


def review_overtime_and_rest(facts: EmployeeFacts, config: ComplianceConfig) -> List[ComplianceFinding]:
    out: List[ComplianceFinding] = []
    if facts.worker_type not in {"employee", "unknown"}:
        return out
    if facts.weekly_hours is not None and facts.weekly_hours > config.regular_weekly_hours:
        out.append(f("WEEKLY_OVERTIME_REVIEW", "Weekly hours exceed regular Israeli weekly benchmark", RiskLevel.HIGH,
                     "Weekly hours exceed the configured regular weekly-hour benchmark and require overtime review.",
                     "Reconcile attendance records and pay statutory overtime premiums where required.",
                     ["Hours of Work and Rest Law, 5711-1951"], {"weekly_hours": facts.weekly_hours}))
    if facts.daily_hours is not None and facts.daily_hours > config.max_daily_hours_including_overtime:
        out.append(f("DAILY_HOURS_CAP", "Daily hours may exceed permitted maximum", RiskLevel.CRITICAL,
                     "Daily hours exceed the configured maximum including overtime.",
                     "Stop scheduling above the cap unless a verified permit or exception applies.",
                     ["Hours of Work and Rest Law, 5711-1951"], {"daily_hours": facts.daily_hours}))
    elif facts.daily_hours is not None and facts.daily_hours > config.regular_daily_hours:
        out.append(f("DAILY_OVERTIME_REVIEW", "Daily hours exceed regular daily benchmark", RiskLevel.MEDIUM,
                     "Daily hours exceed the configured regular daily benchmark and may require overtime premiums.",
                     "Classify daily overtime separately from weekly overtime to avoid underpayment or double counting.",
                     ["Hours of Work and Rest Law, 5711-1951"], {"daily_hours": facts.daily_hours}))
    if facts.overtime_hours_weekly > config.max_weekly_overtime_hours:
        out.append(f("WEEKLY_OVERTIME_CAP", "Weekly overtime exceeds configured cap", RiskLevel.CRITICAL,
                     "Reported weekly overtime exceeds the configured overtime cap.",
                     "Reduce overtime, review permits, and obtain payroll/legal confirmation.",
                     ["Hours of Work and Rest Law, 5711-1951"], {"overtime_hours_weekly": facts.overtime_hours_weekly}))
    if _contains_any(facts.contract_text, [r"includes all overtime", r"unlimited overtime", r"שעות נוספות.*כלול", r"כולל.*כל.*שעות"]):
        out.append(f("GLOBAL_OVERTIME_BLANKET", "Blanket global overtime wording is risky", RiskLevel.HIGH,
                     "The text appears to include all overtime in salary without a clear separate lawful component.",
                     "Use an itemized overtime structure and accurate time records; verify validity for the role.",
                     ["Hours of Work and Rest Law, 5711-1951", "Protection of Wages Law, 5718-1958"], {"text_match": "global overtime"}))
    if _contains_any(facts.contract_text, [r"no overtime", r"not entitled to overtime", r"אינו זכאי.*שעות נוספות"]):
        out.append(f("OVERTIME_WAIVER", "Overtime waiver language is risky", RiskLevel.HIGH,
                     "The text suggests an advance waiver of overtime rights.",
                     "Remove waiver wording and state that statutory overtime applies where required.",
                     ["Hours of Work and Rest Law, 5711-1951"], {"text_match": "overtime waiver"}))
    return out


def review_pension_and_severance(facts: EmployeeFacts, config: ComplianceConfig) -> List[ComplianceFinding]:
    out: List[ComplianceFinding] = []
    if facts.worker_type not in {"employee", "unknown"}:
        return out
    wait = config.pension_waiting_months_with_prior_plan if facts.had_active_pension_before_start else config.pension_waiting_months_without_prior_plan
    if facts.tenure_months >= wait:
        if facts.has_pension_arrangement is False:
            out.append(f("PENSION_MISSING", "Mandatory pension arrangement may be missing", RiskLevel.HIGH,
                         "Tenure appears to exceed the configured pension waiting period, but no pension arrangement is recorded.",
                         "Open or correct pension arrangement and calculate retroactive contributions where required.",
                         ["Mandatory Pension Expansion Order"], {"tenure_months": facts.tenure_months, "waiting_months": wait}))
        if facts.pension_start_month is not None and facts.pension_start_month > wait:
            out.append(f("PENSION_STARTED_LATE", "Pension may have started late", RiskLevel.HIGH,
                         "Recorded pension start month is later than the configured waiting period.",
                         "Check prior active pension status and calculate retroactive contributions.",
                         ["Mandatory Pension Expansion Order"], {"pension_start_month": facts.pension_start_month, "waiting_months": wait}))
    if facts.employer_contribution_pension_pct is not None and facts.employer_contribution_pension_pct < config.employer_pension_min_pct:
        out.append(f("PENSION_EMPLOYER_RATE_LOW", "Employer pension contribution may be too low", RiskLevel.HIGH,
                     "Employer pension contribution is below the configured benchmark.",
                     "Verify current contribution rates and correct contributions.",
                     ["Mandatory Pension Expansion Order"], {"pct": facts.employer_contribution_pension_pct}))
    if facts.employer_contribution_severance_pct is not None and facts.employer_contribution_severance_pct < config.severance_deposit_min_pct:
        out.append(f("SEVERANCE_DEPOSIT_RATE_LOW", "Severance deposit contribution may be too low", RiskLevel.HIGH,
                     "Employer severance contribution is below the configured benchmark.",
                     "Verify applicable contribution rate, Section 14 status, and severance exposure.",
                     ["Severance Pay Law, 5723-1963", "Mandatory Pension Expansion Order"], {"pct": facts.employer_contribution_severance_pct}))
    if facts.has_section_14 and (facts.employer_contribution_severance_pct is None or facts.employer_contribution_severance_pct < config.section_14_full_severance_pct):
        out.append(f("SECTION_14_PARTIAL", "Section 14 arrangement may not fully eliminate severance exposure", RiskLevel.HIGH,
                     "Section 14 is indicated, but full severance deposits or complete terms are not verified.",
                     "Review written Section 14 arrangement, deposit rate, fund release terms, and sector rules.",
                     ["Severance Pay Law, 5723-1963", "Section 14 arrangements"], {"pct": facts.employer_contribution_severance_pct}))
    if _contains_any(facts.contract_text, [r"waive.*severance", r"no severance", r"מוותר.*פיצויי", r"אין.*פיצויי"]):
        out.append(f("SEVERANCE_WAIVER", "Severance waiver wording is risky", RiskLevel.HIGH,
                     "The text suggests waiver or denial of statutory severance rights.",
                     "Remove blanket waiver language and assess severance under law, pension deposits, and Section 14 terms.",
                     ["Severance Pay Law, 5723-1963"], {"text_match": "severance waiver"}))
    return out


def review_notice_and_termination(facts: EmployeeFacts) -> List[ComplianceFinding]:
    out: List[ComplianceFinding] = []
    text = " ".join([facts.termination_reason or "", facts.contract_text or ""])
    termination = bool(facts.termination_reason) or _contains_any(text, [r"termination", r"dismiss", r"fired", r"פיטור", r"סיום העסקה"])
    if not termination:
        return out
    if _contains_any(text, [r"immediate", r"without hearing", r"no hearing", r"לאלתר", r"ללא שימוע"]):
        out.append(f("HEARING_PROCESS_MISSING", "Termination process may lack hearing", RiskLevel.CRITICAL,
                     "The facts suggest dismissal may occur without a prior good-faith hearing.",
                     "Pause termination, issue a proper hearing invitation, consider the response, and document the decision.",
                     ["Israeli Labor Court hearing-duty doctrine", "Advance Notice for Dismissal and Resignation Law, 5761-2001"]))
    required = required_notice_days(facts.tenure_months, monthly_employee=(facts.monthly_salary_ils is not None or facts.hourly_rate_ils is None))
    if facts.notice_days_given is not None and facts.notice_days_given < required:
        out.append(f("NOTICE_SHORTFALL", "Advance notice may be shorter than statutory requirement", RiskLevel.HIGH,
                     "Given notice days are below the estimated statutory notice requirement.",
                     "Provide additional notice or payment in lieu after verifying employee type and tenure.",
                     ["Advance Notice for Dismissal and Resignation Law, 5761-2001"], {"given": facts.notice_days_given, "required": required}))
    if facts.tenure_months >= 12:
        out.append(f("SEVERANCE_ELIGIBILITY_REVIEW", "Severance eligibility requires review", RiskLevel.MEDIUM,
                     "Tenure appears to exceed one year in a termination context.",
                     "Calculate severance exposure and pension-fund release requirements.",
                     ["Severance Pay Law, 5723-1963"], {"tenure_months": facts.tenure_months}))
    return out


def review_protected_status(facts: EmployeeFacts) -> List[ComplianceFinding]:
    out: List[ComplianceFinding] = []
    text = " ".join([facts.termination_reason or "", facts.contract_text or ""])
    protected = facts.is_parent_or_pregnant or facts.is_on_reserve_duty_or_recently_returned or _contains_any(
        text, [r"pregnan", r"fertility", r"parental", r"maternity", r"reserve duty", r"היריון", r"הריון", r"פוריות", r"לידה", r"הורות", r"מילואים"])
    adverse = _contains_any(text, [r"termination", r"dismiss", r"fired", r"reduce", r"demot", r"shift", r"פיטור", r"הפחת", r"צמצ", r"הורדת"])
    if protected and adverse:
        out.append(f("PROTECTED_STATUS_ADVERSE_ACTION", "Adverse action may involve protected status", RiskLevel.CRITICAL,
                     "The facts connect an adverse action to pregnancy, parenthood, fertility treatment, reserve duty, or another protected status.",
                     "Pause action, preserve records, verify permit requirements, and obtain Israeli labor-law review.",
                     ["Women's Employment Law, 5714-1954", "Equal Employment Opportunities Law, 5748-1988"]))
    if _contains_any(text, [r"interview.*pregnan", r"ask.*children", r"שאלה.*היריון", r"שאלה.*ילדים"]):
        out.append(f("HIRING_DISCRIMINATION_QUESTION", "Hiring question may be discriminatory", RiskLevel.HIGH,
                     "The text suggests pregnancy, parenthood, or family-status questions in hiring.",
                     "Remove the question and train interviewers to use role-related criteria only.",
                     ["Equal Employment Opportunities Law, 5748-1988", "Women's Employment Law, 5714-1954"]))
    return out


def review_contractor_status(facts: EmployeeFacts) -> List[ComplianceFinding]:
    if facts.worker_type != "contractor":
        return []
    patterns = [r"fixed hours", r"full time", r"company email", r"manager approval", r"exclusive", r"office", r"personally", r"vacation approval", r"שעות קבועות", r"אישור חופשה", r"בלעדיות"]
    text_score = sum(1 for p in patterns if re.search(p, _norm(facts.contract_text), re.IGNORECASE))
    score = max(facts.contractor_controls, text_score)
    if score >= 4:
        return [f("CONTRACTOR_MISCLASSIFICATION", "Contractor arrangement has employee-status indicators", RiskLevel.HIGH,
                  "The arrangement shows multiple control, integration, or economic-dependence indicators.",
                  "Consider conversion to employment or restructure the supplier relationship around real independence.",
                  ["Israeli Labor Court employee-status tests", "National Insurance and Tax Authority classification guidance"], {"score": score})]
    if score >= 2:
        return [f("CONTRACTOR_STATUS_AMBIGUOUS", "Contractor status needs supporting facts", RiskLevel.MEDIUM,
                  "Some employee-status indicators are present.",
                  "Document deliverables, substitution rights, independent tools, multiple clients, and business risk.",
                  ["Israeli Labor Court employee-status tests"], {"score": score})]
    return []


def review_sector_orders(facts: EmployeeFacts) -> List[ComplianceFinding]:
    sector = _norm(facts.sector)
    terms = ["guarding", "security", "cleaning", "construction", "hospitality", "hotel", "transport", "caregiving", "nursing", "public contractor", "שמירה", "ניקיון", "בנייה", "מלונאות", "הובלה", "סיעוד"]
    if any(t in sector for t in terms):
        return [f("SECTOR_EXPANSION_ORDER_REVIEW", "Sector expansion order may add obligations", RiskLevel.MEDIUM,
                  "The sector may be covered by an expansion order or special arrangement.",
                  "Verify sector-specific wage, pension, training, holiday, seniority, and benefit rules before finalizing.",
                  ["Relevant sector expansion order"], {"sector": facts.sector})]
    return []


def review_text_red_flags(facts: EmployeeFacts) -> List[ComplianceFinding]:
    out: List[ComplianceFinding] = []
    text = facts.contract_text
    if _contains_any(text, [r"waive.*statutory", r"waives all rights", r"waives.*rights", r"מוותר.*זכויות"]):
        out.append(f("STATUTORY_RIGHTS_WAIVER", "Blanket waiver of statutory rights is invalid-risk wording", RiskLevel.HIGH,
                     "The text suggests a waiver of mandatory employment rights.",
                     "Remove waiver language and state that mandatory rights apply despite the policy.",
                     ["Mandatory Israeli labor-law protections"]))
    if _contains_any(text, [r"deduct.*damage", r"deduct.*shortage", r"fine", r"ניכוי.*נזק", r"קנס"]):
        out.append(f("WAGE_DEDUCTION_RISK", "Wage deduction or fine wording is risky", RiskLevel.HIGH,
                     "The text suggests deductions, fines, or penalties from wages.",
                     "Allow deductions only where legally permitted, documented, and processed through payroll.",
                     ["Protection of Wages Law, 5718-1958"]))
    if _contains_any(text, [r"vacation.*forfeit", r"use it or lose it", r"חופשה.*נמחק"]):
        out.append(f("VACATION_FORFEITURE_RISK", "Vacation forfeiture wording needs review", RiskLevel.MEDIUM,
                     "The text may erase vacation rights too broadly.",
                     "Align vacation carryover, use, and redemption wording with Israeli annual-leave rules.",
                     ["Annual Leave Law, 5711-1951"]))
    return out


def missing_facts(facts: EmployeeFacts) -> List[str]:
    missing = []
    if facts.worker_type == "unknown":
        missing.append("Worker type")
    if facts.worker_type in {"employee", "unknown"} and facts.monthly_salary_ils is None and facts.hourly_rate_ils is None:
        missing.append("Wage basis and amount")
    if facts.weekly_hours is None and facts.daily_hours is None:
        missing.append("Actual work hours")
    if facts.tenure_months == 0:
        missing.append("Start date or tenure")
    if facts.sector == "general":
        missing.append("Specific sector if an expansion order might apply")
    return missing


def overall_risk(findings: Sequence[ComplianceFinding]) -> RiskName:
    if not findings:
        return "low"
    return max(finding.risk for finding in findings).label


def review_policy(facts: EmployeeFacts, config: Optional[ComplianceConfig] = None) -> Dict[str, Any]:
    config = config or ComplianceConfig()
    validate_facts(facts)
    findings: List[ComplianceFinding] = []
    for check in [review_minimum_wage, review_overtime_and_rest, review_pension_and_severance]:
        findings.extend(check(facts, config))
    findings.extend(review_notice_and_termination(facts))
    findings.extend(review_protected_status(facts))
    findings.extend(review_contractor_status(facts))
    findings.extend(review_sector_orders(facts))
    findings.extend(review_text_red_flags(facts))
    by_code: Dict[str, ComplianceFinding] = {}
    for item in findings:
        by_code.setdefault(item.code, item)
    ordered = sorted(by_code.values(), key=lambda item: (-int(item.risk), item.code))
    return {
        "overall_risk": overall_risk(ordered),
        "finding_count": len(ordered),
        "findings": [item.to_dict() for item in ordered],
        "missing_facts": missing_facts(facts),
        "config_source_note": config.source_note,
        "disclaimer": "Compliance triage only. Verify current law, rates, and sector orders before action.",
    }


class HRComplianceClient:
    def __init__(self, config: Optional[ComplianceConfig] = None) -> None:
        self.config = config or ComplianceConfig()

    def review(self, facts: EmployeeFacts) -> Dict[str, Any]:
        return review_policy(facts, self.config)

    def review_dict(self, data: Mapping[str, Any]) -> Dict[str, Any]:
        return self.review(EmployeeFacts(**dict(data)))

    def review_json(self, payload: str) -> Dict[str, Any]:
        return self.review_dict(json.loads(payload))

    def review_file(self, path: str | Path) -> Dict[str, Any]:
        return self.review_json(Path(path).read_text(encoding="utf-8"))

    def create_case(
        self,
        data: Mapping[str, Any] | EmployeeFacts,
        case_dir: str | Path = ".hr-compliance-cases",
        environment: ENVIRONMENT = "sandbox",
    ) -> Dict[str, Any]:
        if environment not in {"sandbox", "production"}:
            raise InputValidationError("INVALID_ENVIRONMENT")
        facts_data = asdict(data) if isinstance(data, EmployeeFacts) else dict(data)
        validate_facts(EmployeeFacts(**facts_data))
        case_id = uuid.uuid4().hex[:12]
        target_dir = Path(case_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        payload = {"case_id": case_id, "environment": environment, "facts": facts_data}
        _case_path(target_dir, case_id).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return {"case_id": case_id, "environment": environment, "case_file": str(_case_path(target_dir, case_id))}

    def get_case(self, case_id: str, case_dir: str | Path = ".hr-compliance-cases") -> Dict[str, Any]:
        path = _case_path(case_dir, case_id)
        if not path.exists():
            raise InputValidationError("CASE_NOT_FOUND")
        return json.loads(path.read_text(encoding="utf-8"))

    def review_case(self, case_id: str, case_dir: str | Path = ".hr-compliance-cases") -> Dict[str, Any]:
        case = self.get_case(case_id, case_dir)
        report = self.review_dict(case["facts"])
        report["case_id"] = case_id
        report["environment"] = case.get("environment", "sandbox")
        return report


class AsyncHRComplianceClient:
    def __init__(self, config: Optional[ComplianceConfig] = None) -> None:
        self._client = HRComplianceClient(config)

    async def review(self, facts: EmployeeFacts) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return self._client.review(facts)

    async def review_dict(self, data: Mapping[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return self._client.review_dict(data)

    async def review_json(self, payload: str) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return self._client.review_json(payload)

    async def review_file(self, path: str | Path) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return self._client.review_file(path)

    async def create_case(
        self,
        data: Mapping[str, Any] | EmployeeFacts,
        case_dir: str | Path = ".hr-compliance-cases",
        environment: ENVIRONMENT = "sandbox",
    ) -> Dict[str, Any]:
        await asyncio.sleep(0)
        return self._client.create_case(data, case_dir, environment)

    async def get_case(self, case_id: str, case_dir: str | Path = ".hr-compliance-cases") -> Dict[str, Any]:
        await asyncio.sleep(0)
        return self._client.get_case(case_id, case_dir)

    async def review_case(self, case_id: str, case_dir: str | Path = ".hr-compliance-cases") -> Dict[str, Any]:
        await asyncio.sleep(0)
        return self._client.review_case(case_id, case_dir)


def report_to_markdown(report: Mapping[str, Any]) -> str:
    lines = ["## Compliance snapshot", f"- Overall risk: {report.get('overall_risk')}", f"- Finding count: {report.get('finding_count')}", "", "## Findings"]
    if not report.get("findings"):
        lines.append("- No findings generated from supplied facts.")
    for index, item in enumerate(report.get("findings", []), 1):
        lines += [f"### {index}. [{item.get('risk')}] {item.get('title')}", f"- Code: {item.get('code')}", f"- Explanation: {item.get('explanation')}", f"- Recommendation: {item.get('recommendation')}", f"- Sources to verify: {', '.join(item.get('law_refs', []))}", ""]
    if report.get("missing_facts"):
        lines += ["## Missing facts"] + [f"- {x}" for x in report["missing_facts"]]
    return "\n".join(lines).strip() + "\n"


if __name__ == "__main__":
    demo = EmployeeFacts(worker_type="employee", sector="retail", hourly_rate_ils=31, weekly_hours=46, tenure_months=10, has_pension_arrangement=False, contract_text="Closing time is unpaid.")
    print(json.dumps(review_policy(demo), ensure_ascii=False, indent=2))
