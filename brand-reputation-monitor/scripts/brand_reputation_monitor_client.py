#!/usr/bin/env python3
"""Typed local helper for Hebrew brand reputation monitoring from permitted exports."""

from __future__ import annotations

import asyncio
import csv
import hashlib
import json
import os
import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Iterable, List, Mapping, Optional, Sequence

HEBREW_RE = re.compile(r"[\u0590-\u05FF]")
NIQQUD_RE = re.compile(r"[\u0591-\u05C7]")
EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
PHONE_RE = re.compile(r"(?:(?:\+972|0)(?:-|\s)?(?:[23489]|5\d|7\d)(?:-|\s)?\d{3}(?:-|\s)?\d{4})")
ISRAELI_ID_RE = re.compile(r"\b\d{9}\b")
WHITESPACE_RE = re.compile(r"\s+")

SOURCE_ALIASES = {
    "twitter": "x", "tweet": "x", "x/twitter": "x",
    "facebook.com": "facebook", "fb": "facebook", "meta": "facebook",
    "tik tok": "tiktok", "tik-tok": "tiktok",
    "news": "news_comment", "comment": "news_comment",
    "google": "review", "support": "support_export",
}

POSITIVE_TERMS = {
    "מעולה","מצוין","מצויין","מדהים","מדהימה","מושלם","מושלמת","ממליץ","ממליצה","מומלץ","מומלצת",
    "תודה","תותחים","אלופים","אדיבים","אדיב","טעים","טעימה","נקי","נקייה","מהיר","מהירה",
    "אמינים","אמין","מקצועי","מקצועית","הוגן","הוגנת","וואו","אמאלה","נדיר","נעים","שווה","אחלה","מרוצה","טוב","טובה"
}
NEGATIVE_TERMS = {
    "גרוע","גרועה","זוועה","נורא","נוראי","בושה","אכזבה","מאכזב","מאכזבת","איחור","איחרה","איחרו",
    "איטי","איטית","מלוכלך","מלוכלכת","יקר","יקרה","התעלמות","מתעלמים","שקר","שקרים","גניבה",
    "גנבים","רמאים","חוצפה","מבאס","מביך","לא עונים","אין מענה","לא מומלץ","לא מומלצת","לא להתקרב",
    "חיוב כפול","לא עובד","אין מלאי","הטעיה","מטעה","משפיל","משפילה","לא טוב"
}
URGENT_TERMS = {
    "תביעה","עורך דין","מכתב התראה","חדשות","כתבה","חרם","מסוכן","אלרגיה","הרעלה","הקיא","הקיאה",
    "מקולקל","עובש","פציעה","הטרדה","אפליה","פרטיות","דליפה","נחשף","נחשפה","משטרה",
    "משרד הבריאות","הרשות להגנת הצרכן","רשות להגנת הצרכן","רמאים","גנבים","תז","ת\"ז","זהות",
    "פרטים רפואיים","נתונים אישיים"
}
MIXED_MARKERS = {"אבל","אך","למרות","רק חבל","מצד שני"}
SARCASM_MARKERS = {'"מדהים"', "'מדהים'", "ממש מדהים", "איזה שירות", "כן בטח"}

TOPIC_TERMS = {
    "billing": {"חשבונית","קבלה","זיכוי","חיוב","חיוב כפול","החזר","מע״מ","מעמ","ביטול עסקה","₪"},
    "delivery": {"משלוח","שליח","איחור","איחרה","איחרו","הגעה","הגיע","הגיעה"},
    "support": {"שירות","מענה","לא עונים","טלפון","וואטסאפ","יחס","תגובה"},
    "safety": {"הרעלה","אלרגיה","מסוכן","מקולקל","עובש","הקיא","משרד הבריאות","פציעה"},
    "privacy": {"פרטיות","דליפה","נחשף","נחשפה","תז","ת\"ז","פרטים רפואיים","נתונים אישיים"},
    "campaign": {"קופון","מבצע","השקה","פרסום","אין מלאי","קוד","אותיות קטנות"},
    "pricing": {"מחיר","יקר","זול","שווה","₪","מע״מ","מעמ"},
    "accessibility": {"נגיש","נגישות","קורא מסך","כתוביות"},
    "staff": {"עובד","עובדת","צוות","מנהל","מנהלת","משפיל","משפילה"},
    "legal": {"תביעה","עורך דין","מכתב התראה","משטרה","חוקי"},
    "media": {"חדשות","כתבה","עיתונאי","עיתונאית","תחקיר"},
}

@dataclass(frozen=True)
class Mention:
    text: str
    source: str = "unknown"
    date: Optional[str] = None
    brand: Optional[str] = None
    author: Optional[str] = None
    url: Optional[str] = None
    engagement: int = 0
    topic: Optional[str] = None
    branch: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any], text_field: str = "text") -> "Mention":
        text = str(row.get(text_field, "") or "").strip()
        if not text:
            raise ValueError("TEXT_FIELD_MISSING")
        known = {"text", text_field, "source", "date", "brand", "author", "url", "engagement", "topic", "branch"}
        return cls(
            text=text,
            source=normalize_source(str(row.get("source", "unknown") or "unknown")),
            date=normalize_date(row.get("date")),
            brand=clean_optional(row.get("brand")),
            author=clean_optional(row.get("author")),
            url=clean_optional(row.get("url")),
            engagement=parse_engagement(row.get("engagement", 0)),
            topic=clean_optional(row.get("topic")),
            branch=clean_optional(row.get("branch")),
            metadata={str(k): v for k, v in row.items() if k not in known},
        )

@dataclass(frozen=True)
class SentimentResult:
    label: str
    score: float
    confidence: str
    positive_hits: List[str]
    negative_hits: List[str]
    urgent_hits: List[str]
    mixed: bool = False

@dataclass(frozen=True)
class AnalysisResult:
    mention: Mention
    sentiment: SentimentResult
    topics: List[str]
    risk_score: int
    urgency: bool
    recommended_action: str
    redacted_text: str
    fingerprint: str
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mention": asdict(self.mention),
            "sentiment": asdict(self.sentiment),
            "topics": self.topics,
            "risk_score": self.risk_score,
            "urgency": self.urgency,
            "recommended_action": self.recommended_action,
            "redacted_text": self.redacted_text,
            "fingerprint": self.fingerprint,
        }

@dataclass
class MonitorConfig:
    brand_terms: List[str] = field(default_factory=list)
    exclude_terms: List[str] = field(default_factory=list)
    urgent_engagement_threshold: int = 50
    high_risk_engagement_threshold: int = 25
    require_brand_match: bool = False
    locale: str = "he-IL"
    currency: str = "₪"
    date_format: str = "DD/MM/YYYY"

def clean_optional(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text or None

def parse_engagement(value: Any) -> int:
    if value is None or value == "":
        return 0
    try:
        if isinstance(value, str):
            value = value.replace(",", "").strip()
        return max(0, int(float(value)))
    except (TypeError, ValueError) as exc:
        raise ValueError("INVALID_ENGAGEMENT") from exc

def normalize_source(source: str) -> str:
    value = source.strip().lower().replace("_comments", "_comment")
    return SOURCE_ALIASES.get(value, value or "unknown")

def normalize_date(value: Any) -> Optional[str]:
    if value is None or value == "":
        return None
    text = str(value).strip()
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(text[:10], fmt).strftime("%d/%m/%Y")
        except ValueError:
            pass
    return text

def strip_niqqud(text: str) -> str:
    return NIQQUD_RE.sub("", text)

def normalize_hebrew(text: str) -> str:
    text = strip_niqqud(text)
    text = text.replace("״", '"').replace("׳", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"[!?.]{2,}", " ", text)
    text = WHITESPACE_RE.sub(" ", text)
    return text.strip().lower()

def detect_language(text: str) -> str:
    if not text:
        return "unknown"
    hebrew = len(HEBREW_RE.findall(text))
    letters = sum(1 for ch in text if ch.isalpha())
    if letters == 0:
        return "unknown"
    ratio = hebrew / letters
    if ratio > 0.6:
        return "he"
    if ratio > 0.15:
        return "mixed"
    return "en"

def contains_term(text: str, term: str) -> bool:
    normalized = normalize_hebrew(text)
    term_norm = normalize_hebrew(term)
    if not term_norm:
        return False
    if " " in term_norm:
        return term_norm in normalized
    return re.search(rf"(^|[\s\"'.,;:!?()\[\]{{}}])(?:[ובכלמהש])?{re.escape(term_norm)}($|[\s\"'.,;:!?()\[\]{{}}])", normalized) is not None

def find_terms(text: str, terms: Iterable[str]) -> List[str]:
    return sorted({term for term in terms if contains_term(text, term)}, key=lambda x: (len(x), x))

def has_negated_positive(text: str) -> bool:
    normalized = normalize_hebrew(text)
    for pos in POSITIVE_TERMS:
        if re.search(rf"(לא|בכלל לא|לא ממש)\s+{re.escape(normalize_hebrew(pos))}", normalized):
            return True
    return False

def has_positive_negation_phrase(text: str) -> bool:
    normalized = normalize_hebrew(text)
    return any(phrase in normalized for phrase in ("לא רע", "לא רע בכלל", "לא גרוע", "לא נורא"))

def detect_sarcasm(text: str) -> bool:
    normalized = normalize_hebrew(text)
    if any(marker in normalized for marker in SARCASM_MARKERS):
        return True
    return bool(re.search(r'"[^"]*(מדהים|מצוין|מעולה)[^"]*"', normalized) and find_terms(text, NEGATIVE_TERMS))

def redact_private_data(text: str) -> str:
    return ISRAELI_ID_RE.sub("[ID]", PHONE_RE.sub("[PHONE]", EMAIL_RE.sub("[EMAIL]", text)))

def analyze_sentiment(text: str) -> SentimentResult:
    normalized = normalize_hebrew(text)
    positive_hits = find_terms(normalized, POSITIVE_TERMS)
    negative_hits = find_terms(normalized, NEGATIVE_TERMS)
    urgent_hits = find_terms(normalized, URGENT_TERMS)
    score = 0.28 * len(positive_hits) - 0.34 * len(negative_hits) - 0.45 * len(urgent_hits)
    if has_positive_negation_phrase(normalized):
        score += 0.35
    if has_negated_positive(normalized):
        score -= 0.45
    sarcasm = detect_sarcasm(normalized)
    if sarcasm:
        score -= 0.55
    mixed = bool(positive_hits and negative_hits) or any(marker in normalized for marker in MIXED_MARKERS)
    if mixed and positive_hits and negative_hits:
        score *= 0.55
    score = max(-1.0, min(1.0, score))
    if urgent_hits and (negative_hits or score < -0.2 or any(term in normalized for term in ("פרטיות", "הרעלה", "אלרגיה", "תביעה", "משרד הבריאות"))):
        label = "urgent"
    elif mixed and positive_hits and (negative_hits or "אבל" in normalized or "למרות" in normalized):
        label = "mixed"
    elif score >= 0.22:
        label = "positive"
    elif score <= -0.22:
        label = "negative"
    else:
        label = "neutral"
    evidence_count = len(positive_hits) + len(negative_hits) + len(urgent_hits)
    confidence = "medium" if sarcasm or mixed else ("high" if evidence_count >= 2 else ("medium" if evidence_count == 1 else "low"))
    return SentimentResult(label, round(score, 3), confidence, positive_hits, negative_hits, urgent_hits, mixed)

def extract_topics(text: str) -> List[str]:
    normalized = normalize_hebrew(text)
    topics = [topic for topic, terms in TOPIC_TERMS.items() if find_terms(normalized, terms)]
    if not topics and "?" in text:
        topics.append("info")
    if not topics:
        topics.append("general")
    return topics

def compute_risk(mention: Mention, sentiment: SentimentResult, topics: Sequence[str], config: Optional[MonitorConfig] = None) -> int:
    config = config or MonitorConfig()
    score = {"urgent": 55, "negative": 35, "mixed": 20, "positive": 0, "neutral": 5}.get(sentiment.label, 5)
    if any(t in topics for t in ("safety", "privacy", "legal", "media")):
        score += 25
    if "billing" in topics:
        score += 12
    if mention.engagement >= config.urgent_engagement_threshold:
        score += 20
    elif mention.engagement >= config.high_risk_engagement_threshold:
        score += 12
    elif mention.engagement >= 10:
        score += 6
    if mention.source in {"news_comment", "x", "tiktok"} and sentiment.label in {"negative", "urgent"}:
        score += 5
    if mention.url:
        score += 3
    return int(max(0, min(100, score)))

def recommend_action(risk_score: int, sentiment: SentimentResult, topics: Sequence[str]) -> str:
    topic_set = set(topics)
    if sentiment.label == "positive":
        return "Log praise; consider a short thank-you reply"
    if sentiment.label == "neutral" and "info" in topic_set:
        return "Answer the factual question if the source permits"
    if risk_score >= 75:
        return "Immediate escalation; preserve evidence; prepare formal response"
    if topic_set & {"safety", "privacy", "legal", "media"}:
        return "Escalate for management and qualified review before detailed public response"
    if "billing" in topic_set:
        return "Route to accounting/support; request details privately"
    if risk_score >= 50:
        return "Escalate to manager and respond within business day"
    if risk_score >= 25:
        return "Reply if public response would help; route to support"
    return "Log only; monitor for repeated pattern"

def fingerprint_mention(mention: Mention) -> str:
    base = "|".join([mention.source, mention.date or "", normalize_hebrew(mention.text), mention.url or ""])
    return hashlib.sha256(base.encode("utf-8")).hexdigest()[:16]

class BrandReputationMonitor:
    """Analyze supplied brand-mention records."""

    def __init__(self, config: Optional[MonitorConfig] = None) -> None:
        self.config = config or MonitorConfig()

    def is_brand_match(self, text: str) -> bool:
        if not self.config.brand_terms:
            return True
        return any(contains_term(text, term) for term in self.config.brand_terms)

    def is_excluded(self, text: str) -> bool:
        return any(contains_term(text, term) for term in self.config.exclude_terms)

    def analyze_mention(self, mention: Mention) -> AnalysisResult:
        if self.config.require_brand_match and not self.is_brand_match(mention.text):
            sentiment = SentimentResult("neutral", 0.0, "low", [], [], [], False)
            return AnalysisResult(mention, sentiment, ["false_positive"], 0, False, "Exclude unless another brand signal is present", redact_private_data(mention.text), fingerprint_mention(mention))
        if self.is_excluded(mention.text):
            sentiment = SentimentResult("neutral", 0.0, "low", [], [], [], False)
            return AnalysisResult(mention, sentiment, ["excluded"], 0, False, "Excluded by configured term", redact_private_data(mention.text), fingerprint_mention(mention))
        sentiment = analyze_sentiment(mention.text)
        topics = extract_topics(mention.text)
        risk = compute_risk(mention, sentiment, topics, self.config)
        return AnalysisResult(mention, sentiment, topics, risk, sentiment.label == "urgent" or risk >= 75, recommend_action(risk, sentiment, topics), redact_private_data(mention.text), fingerprint_mention(mention))

    def analyze_many(self, mentions: Iterable[Mention]) -> List[AnalysisResult]:
        return [self.analyze_mention(m) for m in mentions]

    async def analyze_mention_async(self, mention: Mention) -> AnalysisResult:
        return await asyncio.to_thread(self.analyze_mention, mention)

    async def analyze_many_async(self, mentions: Iterable[Mention]) -> List[AnalysisResult]:
        tasks = [self.analyze_mention_async(m) for m in mentions]
        return list(await asyncio.gather(*tasks)) if tasks else []

    def summarize(self, results: Sequence[AnalysisResult]) -> Dict[str, Any]:
        labels = Counter(r.sentiment.label for r in results)
        topics = Counter(t for r in results for t in r.topics)
        sources = Counter(r.mention.source for r in results)
        urgent = [r for r in results if r.urgency]
        avg = round(sum(r.risk_score for r in results) / len(results), 2) if results else 0.0
        return {"total": len(results), "sentiment": dict(labels), "topics": dict(topics), "sources": dict(sources), "urgent_count": len(urgent), "average_risk": avg, "top_risk": [r.to_dict() for r in sorted(results, key=lambda r: r.risk_score, reverse=True)[:5]]}

    def generate_markdown_report(self, results: Sequence[AnalysisResult], title: str = "Brand Reputation Report") -> str:
        summary = self.summarize(results)
        lines = [f"# {title}", "", f"Generated: {date.today().strftime('%d/%m/%Y')}", f"Total mentions: {summary['total']}", f"Urgent mentions: {summary['urgent_count']}", f"Average risk: {summary['average_risk']}", "", "## Sentiment"]
        for label in ("positive", "mixed", "neutral", "negative", "urgent"):
            lines.append(f"- {label}: {summary['sentiment'].get(label, 0)}")
        lines += ["", "## Top topics"]
        for topic, count in Counter(summary["topics"]).most_common(10):
            lines.append(f"- {topic}: {count}")
        lines += ["", "## Highest-risk mentions"]
        for result in sorted(results, key=lambda r: r.risk_score, reverse=True)[:10]:
            lines += ["", f"### Risk {result.risk_score} — {result.sentiment.label}", f"- Source: {result.mention.source}", f"- Topics: {', '.join(result.topics)}", f"- Action: {result.recommended_action}", f"- Text: {result.redacted_text}"]
            if result.mention.date:
                lines.insert(-3, f"- Date: {result.mention.date}")
        return "\n".join(lines) + "\n"

def default_config_dir(env: str = "sandbox") -> Path:
    """Return the local configuration directory for the selected environment."""
    safe_env = "production" if env == "production" else "sandbox"
    return Path(os.environ.get("BRM_CONFIG_DIR", str(Path.home() / ".brand_reputation_monitor"))) / safe_env / "configs"


def create_monitor_config(
    name: str,
    env: str = "sandbox",
    brand_terms: Optional[Sequence[str]] = None,
    exclude_terms: Optional[Sequence[str]] = None,
    require_brand_match: bool = False,
) -> Dict[str, Any]:
    """Create a local monitoring configuration and return its identifier."""
    seed = "|".join([name, env, ",".join(brand_terms or []), ",".join(exclude_terms or [])])
    config_id = "brm_" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]
    directory = default_config_dir(env)
    directory.mkdir(parents=True, exist_ok=True)
    payload = {
        "id": config_id,
        "name": name,
        "env": "production" if env == "production" else "sandbox",
        "brand_terms": list(brand_terms or []),
        "exclude_terms": list(exclude_terms or []),
        "require_brand_match": bool(require_brand_match),
        "date_format": "DD/MM/YYYY",
        "currency": "₪",
        "config_path": str(directory / f"{config_id}.json"),
    }
    Path(payload["config_path"]).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def load_monitor_config(config_id: str, env: str = "sandbox") -> MonitorConfig:
    """Load a local monitoring configuration by identifier."""
    path = default_config_dir(env) / f"{config_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"CONFIG_NOT_FOUND: {config_id}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return MonitorConfig(
        brand_terms=list(payload.get("brand_terms", [])),
        exclude_terms=list(payload.get("exclude_terms", [])),
        require_brand_match=bool(payload.get("require_brand_match", False)),
        date_format=str(payload.get("date_format", "DD/MM/YYYY")),
        currency=str(payload.get("currency", "₪")),
    )


def load_mentions(path: str | Path, text_field: str = "text") -> List[Mention]:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError("INPUT_MISSING")
    suffix = source.suffix.lower()
    if suffix == ".csv":
        try:
            with source.open("r", encoding="utf-8-sig", newline="") as fh:
                return [Mention.from_mapping(row, text_field=text_field) for row in csv.DictReader(fh) if any(row.values())]
        except UnicodeDecodeError as exc:
            raise ValueError("BAD_ENCODING") from exc
    if suffix == ".json":
        try:
            payload = json.loads(source.read_text(encoding="utf-8-sig"))
        except UnicodeDecodeError as exc:
            raise ValueError("BAD_ENCODING") from exc
        records = payload.get("mentions", []) if isinstance(payload, dict) else payload
        if not isinstance(records, list):
            raise ValueError("UNSUPPORTED_FORMAT")
        return [Mention.from_mapping(record, text_field=text_field) for record in records]
    if suffix == ".jsonl":
        try:
            return [Mention.from_mapping(json.loads(line), text_field=text_field) for line in source.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
        except UnicodeDecodeError as exc:
            raise ValueError("BAD_ENCODING") from exc
    raise ValueError("UNSUPPORTED_FORMAT")

def dump_results(results: Sequence[AnalysisResult], path: str | Path, fmt: str = "json") -> None:
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        dest.write_text(json.dumps([r.to_dict() for r in results], ensure_ascii=False, indent=2), encoding="utf-8")
    elif fmt == "jsonl":
        dest.write_text("".join(json.dumps(r.to_dict(), ensure_ascii=False) + "\n" for r in results), encoding="utf-8")
    elif fmt == "csv":
        fields = ["date","source","sentiment","score","confidence","risk_score","urgency","topics","recommended_action","redacted_text","url"]
        with dest.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            for r in results:
                writer.writerow({"date": r.mention.date or "", "source": r.mention.source, "sentiment": r.sentiment.label, "score": r.sentiment.score, "confidence": r.sentiment.confidence, "risk_score": r.risk_score, "urgency": r.urgency, "topics": ",".join(r.topics), "recommended_action": r.recommended_action, "redacted_text": r.redacted_text, "url": r.mention.url or ""})
    else:
        raise ValueError("UNSUPPORTED_FORMAT")

def deduplicate_mentions(mentions: Iterable[Mention]) -> List[Mention]:
    seen: Dict[str, Mention] = {}
    for mention in mentions:
        key = fingerprint_mention(mention)
        if key not in seen or mention.engagement > seen[key].engagement:
            seen[key] = mention
    return list(seen.values())

async def stream_analyze_jsonl(path: str | Path, monitor: Optional[BrandReputationMonitor] = None) -> AsyncIterator[AnalysisResult]:
    monitor = monitor or BrandReputationMonitor()
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError("INPUT_MISSING")
    with source.open("r", encoding="utf-8-sig") as fh:
        for line in fh:
            if line.strip():
                yield await monitor.analyze_mention_async(Mention.from_mapping(json.loads(line)))

__all__ = ["AnalysisResult","BrandReputationMonitor","Mention","MonitorConfig","SentimentResult","analyze_sentiment","compute_risk","deduplicate_mentions","detect_language","dump_results","extract_topics","load_mentions","normalize_date","normalize_hebrew","normalize_source","parse_engagement","redact_private_data","stream_analyze_jsonl"]
