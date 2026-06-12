#!/usr/bin/env python3
"""Structured Hebrew chat data analyzer.

Provides a dependency-light sync and async client for analyzing Hebrew and mixed Hebrew-English
customer conversations. The implementation favors transparent heuristics that can be reviewed,
tested, and customized for Israeli small-business workflows.
"""

from __future__ import annotations

import asyncio
import csv
import datetime as _dt
import hashlib
import io
import json
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Iterable, Iterator, List, Mapping, MutableMapping, Optional, Sequence, Tuple, Union


HEBREW_RE = re.compile(r"[\u0590-\u05FF]")
HEBREW_WORD_RE = re.compile(r"[\u0590-\u05FF]{2,}|[A-Za-z]{2,}|\d+(?:[.,]\d+)?")
NIQQUD_RE = re.compile(r"[\u0591-\u05C7]")
RTL_MARKS_RE = re.compile(r"[\u200e\u200f\u202a-\u202e]")
EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+972[-\s]?)?0?5\d[-\s]?\d{3}[-\s]?\d{4}(?!\d)")
CREDIT_CARD_RE = re.compile(r"(?<!\d)(?:\d[ -]*?){13,19}(?!\d)")
ISRAELI_ID_RE = re.compile(r"(?<!\d)\d{9}(?!\d)")
URL_RE = re.compile(r"https?://\S+|www\.\S+", re.I)
QUESTION_RE = re.compile(r"[?？]|(?:\bמה\b|\bאיך\b|\bכמה\b|\bמתי\b|\bלמה\b|\bאיפה\b|\bהאם\b)")

DEFAULT_TIME_FORMATS = (
    "%Y-%m-%dT%H:%M:%S%z",
    "%Y-%m-%dT%H:%M:%S.%f%z",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%d-%m-%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%d/%m/%Y %H:%M:%S",
)

POSITIVE_TERMS = {
    "תודה", "תודה רבה", "מעולה", "מצוין", "מצויין", "נהדר", "אחלה", "סבבה",
    "טוב", "מרוצה", "מרוצים", "עזר", "עזרת", "פתרת", "נפתר", "שמח", "שמחה",
    "אהבתי", "מקצועי", "מקצועית", "מהיר", "מהירה", "מושלם", "מושלמת", "יעיל",
    "יעילה", "ממליץ", "ממליצה", "הסתדר", "הסתדרה", "ברור", "ברורה", "קל",
    "קלה", "fantastic", "great", "thanks", "thank", "good", "excellent", "resolved",
}
NEGATIVE_TERMS = {
    "לא טוב", "גרוע", "גרועה", "מאכזב", "מאכזבת", "בעיה", "תקלה", "לא עובד",
    "לא עובדת", "כועס", "כועסת", "עצבים", "חוצפה", "בושה", "זוועה", "דחוף",
    "איטי", "איטית", "ממתין", "ממתינה", "חיכיתי", "מחכה", "יקר", "יקרה",
    "הטעיה", "רמאות", "לבטל", "ביטול", "החזר", "פיצוי", "תלונה", "מתלונן",
    "מתלוננת", "מאיים", "איום", "תביעה", "עו״ד", "עורך דין", "לא מרוצה",
    "לא מרוצה", "לא תקין", "לא תקינה", "נמאס", "כשל", "נפל", "crash", "bad",
    "angry", "refund", "cancel", "complaint", "urgent", "broken", "terrible",
}
NEGATIONS = {"לא", "בלי", "אינו", "אינה", "אין", "אל", "לאו", "never", "not", "no"}
INTENSIFIERS = {"מאוד", "ממש", "לגמרי", "דחוף", "בהקדם", "עכשיו", "מאד", "very", "urgent"}

INTENT_KEYWORDS: Dict[str, Sequence[str]] = {
    "billing_tax": (
        "חשבונית", "קבלה", "חשבוניות", "קבלות", "מס", "מע״מ", "מע\"מ", "מעמ",
        "עוסק פטור", "עוסק מורשה", "ח.פ", "חפ", "מספר עוסק", "תשלום", "שילמתי",
        "חיוב", "זיכוי", "תעודת משלוח", "הצעת מחיר", "מחיר", "עלות", "₪", "שח",
        "invoice", "receipt", "vat", "tax", "payment", "charge",
    ),
    "appointment": (
        "תור", "לקבוע", "זימון", "פגישה", "מועד", "תאריך", "שעה", "להזיז",
        "לדחות", "להקדים", "יומן", "תזכורת", "appointment", "meeting", "schedule",
    ),
    "delivery": (
        "משלוח", "שליח", "איסוף", "מסירה", "הגיע", "הגיעה", "חבילה", "מספר מעקב",
        "דואר", "צ׳יטה", "ציטה", "שליחות", "delivery", "shipment", "tracking",
    ),
    "cancellation_refund": (
        "ביטול", "לבטל", "החזר", "להחזיר", "זיכוי", "עסקה", "חרטה", "התחרטתי",
        "ביטול עסקה", "refund", "cancel", "return",
    ),
    "product_info": (
        "מידה", "צבע", "מלאי", "זמין", "זמינות", "מפרט", "אחריות", "דגם",
        "כמה עולה", "איזה", "מה ההבדל", "product", "stock", "warranty",
    ),
    "complaint": (
        "תלונה", "לא מרוצה", "גרוע", "חוצפה", "בושה", "זוועה", "שירות גרוע",
        "פיצוי", "מנהל", "מנהלת", "complaint", "manager",
    ),
    "technical_support": (
        "תקלה", "לא עובד", "לא עובדת", "שגיאה", "קוד", "סיסמה", "התחברות",
        "אפליקציה", "אתר", "נפל", "קרס", "bug", "error", "login", "password",
    ),
    "sales_lead": (
        "מעוניין", "מעוניינת", "רוצה לקנות", "הצעת מחיר", "מחירון", "דמו",
        "חבילה", "מבצע", "לרכוש", "לקנות", "quote", "pricing", "demo", "buy",
    ),
    "legal_privacy": (
        "פרטיות", "הסכמה", "מחיקה", "מאגר מידע", "ספאם", "דיוור", "הסר",
        "תביעה", "עו״ד", "עורך דין", "זכויות", "privacy", "consent", "unsubscribe",
    ),
    "human_agent": (
        "נציג", "נציגה", "מענה אנושי", "בן אדם", "אדם", "מנהל", "מנהלת",
        "שירות לקוחות", "דברו איתי", "תחזרו אליי", "agent", "human",
    ),
    "small_talk": (
        "שלום", "היי", "בוקר טוב", "ערב טוב", "מה נשמע", "תודה", "להתראות",
        "hi", "hello", "bye", "thanks",
    ),
}

RESOLUTION_TERMS = {
    "תודה", "תודה רבה", "הסתדר", "הסתדרה", "מעולה", "נפתר", "פתרת", "עזרת",
    "סגור", "סגורה", "אפשר לסגור", "תודה יום טוב", "resolved", "thanks", "solved",
}

SENSITIVE_LABELS = {
    "email": EMAIL_RE,
    "phone": PHONE_RE,
    "credit_card_like": CREDIT_CARD_RE,
    "israeli_id_like": ISRAELI_ID_RE,
    "url": URL_RE,
}


@dataclass(frozen=True)
class ChatMessage:
    """Single customer-chat message."""

    sender: str
    text: str
    timestamp: Optional[str] = None
    message_id: Optional[str] = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SentimentScore:
    """Transparent sentiment score."""

    label: str
    score: float
    positive_hits: int
    negative_hits: int
    evidence: Tuple[str, ...]


@dataclass(frozen=True)
class IntentScore:
    """Intent score with matched terms."""

    intent: str
    score: float
    hits: Tuple[str, ...]


@dataclass(frozen=True)
class ConversationAnalysis:
    """Result for one conversation."""

    session_id: str
    language: str
    primary_intent: str
    intent_scores: Tuple[IntentScore, ...]
    sentiment: SentimentScore
    risk_flags: Mapping[str, int]
    message_count: int
    user_message_count: int
    bot_message_count: int
    first_response_seconds: Optional[float]
    average_response_seconds: Optional[float]
    drop_off: bool
    escalation_requested: bool
    unresolved: bool
    resolution_status: str
    question_count: int
    top_terms: Tuple[Tuple[str, int], ...]
    recommendations: Tuple[str, ...]


@dataclass(frozen=True)
class DatasetAnalysis:
    """Aggregate result for multiple conversations."""

    conversation_count: int
    total_messages: int
    language_distribution: Mapping[str, int]
    sentiment_distribution: Mapping[str, int]
    intent_distribution: Mapping[str, int]
    risk_flag_totals: Mapping[str, int]
    drop_off_rate: float
    escalation_rate: float
    unresolved_rate: float
    average_first_response_seconds: Optional[float]
    recommendations: Tuple[str, ...]
    conversations: Tuple[ConversationAnalysis, ...]


class ValidationError(ValueError):
    """Raised when conversation input cannot be parsed."""


def normalize_hebrew(text: str) -> str:
    """Normalize Hebrew text without transliterating it."""

    if text is None:
        return ""
    normalized = str(text)
    normalized = RTL_MARKS_RE.sub("", normalized)
    normalized = NIQQUD_RE.sub("", normalized)
    normalized = normalized.replace("׳", "'").replace("״", '"')
    normalized = normalized.replace("\u00a0", " ")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def tokenize(text: str) -> List[str]:
    """Tokenize Hebrew, English, and numeric mentions."""

    return [t.lower() for t in HEBREW_WORD_RE.findall(normalize_hebrew(text))]


def parse_timestamp(value: Optional[Union[str, _dt.datetime]]) -> Optional[_dt.datetime]:
    """Parse common chat timestamp formats, including Israeli DD-MM-YYYY formats."""

    if value in (None, ""):
        return None
    if isinstance(value, _dt.datetime):
        return value
    raw = str(value).strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        return _dt.datetime.fromisoformat(raw)
    except ValueError:
        pass
    for fmt in DEFAULT_TIME_FORMATS:
        try:
            return _dt.datetime.strptime(raw, fmt)
        except ValueError:
            continue
    raise ValidationError(f"Unsupported timestamp format: {value!r}")


def detect_language(text: str) -> str:
    """Return he, en, mixed, or unknown."""

    clean = normalize_hebrew(text)
    if not clean:
        return "unknown"
    hebrew_chars = len(HEBREW_RE.findall(clean))
    latin_chars = len(re.findall(r"[A-Za-z]", clean))
    total_letters = hebrew_chars + latin_chars
    if total_letters == 0:
        return "unknown"
    if hebrew_chars and latin_chars:
        return "mixed"
    if hebrew_chars:
        return "he"
    if latin_chars:
        return "en"
    return "unknown"


def _phrase_hits(text: str, terms: Iterable[str]) -> List[str]:
    clean = normalize_hebrew(text).lower()
    clean_tokens = tokenize(clean)
    hits: List[str] = []
    for term in terms:
        term_clean = normalize_hebrew(term).lower()
        if not term_clean:
            continue
        if " " in term_clean or '"' in term_clean or "״" in term:
            if term_clean in clean:
                hits.append(term)
            continue
        has_hebrew = bool(HEBREW_RE.search(term_clean))
        if has_hebrew:
            # Hebrew customer messages often attach one-letter prefixes such as ב/ל/כ/מ/ה/ו.
            # Match exact tokens and short-prefixed forms like "במנוי" or "הפרימיום".
            for token in clean_tokens:
                if token == term_clean or (token.endswith(term_clean) and 0 < len(token) - len(term_clean) <= 2):
                    hits.append(term)
                    break
        elif term_clean in clean_tokens:
            hits.append(term)
    return hits


def sentiment_score(text: str) -> SentimentScore:
    """Score sentiment using Hebrew-aware lexicons and simple negation handling."""

    clean = normalize_hebrew(text).lower()
    tokens = tokenize(clean)
    evidence: List[str] = []

    positive_hits = _phrase_hits(clean, POSITIVE_TERMS)
    negative_hits = _phrase_hits(clean, NEGATIVE_TERMS)

    positive = len(positive_hits)
    negative = len(negative_hits)
    evidence.extend([f"+:{h}" for h in positive_hits[:8]])
    evidence.extend([f"-:{h}" for h in negative_hits[:8]])

    for i, token in enumerate(tokens[:-1]):
        if token in NEGATIONS:
            window = " ".join(tokens[i + 1 : i + 4])
            if any(term in window for term in ("טוב", "מרוצה", "עובד", "תקין", "ברור", "good", "working")):
                negative += 1
                evidence.append(f"-:negation:{token} {window}")
            if any(term in window for term in ("גרוע", "בעיה", "תקלה", "bad", "terrible")):
                positive += 1
                evidence.append(f"+:negated-negative:{token} {window}")

    intensity = 1 + min(sum(1 for token in tokens if token in INTENSIFIERS), 3) * 0.25
    raw = (positive - negative) * intensity
    score = max(-1.0, min(1.0, raw / 4.0))
    if score >= 0.2:
        label = "positive"
    elif score <= -0.2:
        label = "negative"
    else:
        label = "neutral"
    return SentimentScore(label=label, score=round(score, 3), positive_hits=positive, negative_hits=negative, evidence=tuple(evidence[:12]))


def classify_intent(text: str, custom_keywords: Optional[Mapping[str, Sequence[str]]] = None) -> Tuple[IntentScore, ...]:
    """Classify customer intent using weighted keyword matches."""

    merged: Dict[str, Sequence[str]] = dict(INTENT_KEYWORDS)
    if custom_keywords:
        for intent, terms in custom_keywords.items():
            merged[intent] = tuple(terms)
    clean = normalize_hebrew(text).lower()
    scores: List[IntentScore] = []
    for intent, terms in merged.items():
        hits = _phrase_hits(clean, terms)
        if not hits:
            continue
        phrase_bonus = sum(0.5 for hit in hits if " " in hit)
        score = len(set(hits)) + phrase_bonus
        scores.append(IntentScore(intent=intent, score=round(score, 3), hits=tuple(dict.fromkeys(hits))))
    scores.sort(key=lambda s: (-s.score, s.intent))
    if not scores:
        return (IntentScore(intent="unknown", score=0.0, hits=()),)
    return tuple(scores)


def detect_sensitive_data(text: str) -> Dict[str, int]:
    """Detect sensitive-data patterns that require minimization or masking."""

    clean = normalize_hebrew(text)
    results: Dict[str, int] = {}
    for label, pattern in SENSITIVE_LABELS.items():
        hits = pattern.findall(clean)
        if label == "credit_card_like":
            hits = [hit for hit in hits if _passes_luhn(re.sub(r"\D", "", hit))]
        if label == "israeli_id_like":
            hits = [hit for hit in hits if _valid_israeli_id(hit)]
        if hits:
            results[label] = len(hits)
    return results


def anonymize_text(text: str) -> str:
    """Mask common identifiers while preserving analytical value."""

    masked = normalize_hebrew(text)
    masked = EMAIL_RE.sub("[EMAIL]", masked)
    masked = PHONE_RE.sub("[PHONE]", masked)

    def _mask_card(match: re.Match[str]) -> str:
        digits = re.sub(r"\D", "", match.group(0))
        if len(digits) >= 13 and _passes_luhn(digits):
            return "[CARD]"
        return match.group(0)

    def _mask_id(match: re.Match[str]) -> str:
        raw = match.group(0)
        return "[ISRAELI_ID]" if _valid_israeli_id(raw) else raw

    masked = CREDIT_CARD_RE.sub(_mask_card, masked)
    masked = ISRAELI_ID_RE.sub(_mask_id, masked)
    return masked


def _passes_luhn(number: str) -> bool:
    if not number or not number.isdigit() or len(number) < 13:
        return False
    total = 0
    reverse_digits = number[::-1]
    for i, ch in enumerate(reverse_digits):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def _valid_israeli_id(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    if len(digits) != 9:
        return False
    total = 0
    for i, ch in enumerate(digits):
        n = int(ch) * (1 if i % 2 == 0 else 2)
        total += n if n < 10 else n - 9
    return total % 10 == 0


def _coerce_message(raw: Union[ChatMessage, Mapping[str, Any]]) -> ChatMessage:
    if isinstance(raw, ChatMessage):
        return raw
    if not isinstance(raw, Mapping):
        raise ValidationError("Each message must be a mapping or ChatMessage.")
    sender = str(raw.get("sender") or raw.get("role") or "").lower().strip()
    if sender in {"customer", "client", "user_customer"}:
        sender = "user"
    if sender in {"assistant", "agent", "business", "system_bot"}:
        sender = "bot"
    if sender not in {"user", "bot", "system"}:
        raise ValidationError(f"Unsupported sender: {sender!r}")
    text = raw.get("text", raw.get("message", raw.get("body", "")))
    if text is None:
        text = ""
    return ChatMessage(
        sender=sender,
        text=str(text),
        timestamp=raw.get("timestamp") or raw.get("time") or raw.get("created_at"),
        message_id=raw.get("message_id") or raw.get("id"),
        metadata={k: v for k, v in raw.items() if k not in {"sender", "role", "text", "message", "body", "timestamp", "time", "created_at", "message_id", "id"}},
    )


def validate_conversation(messages: Sequence[Union[ChatMessage, Mapping[str, Any]]]) -> None:
    """Validate minimum conversation shape."""

    if not isinstance(messages, Sequence) or isinstance(messages, (str, bytes)):
        raise ValidationError("Conversation messages must be a sequence.")
    if not messages:
        raise ValidationError("Conversation must contain at least one message.")
    for item in messages:
        message = _coerce_message(item)
        if message.sender in {"user", "bot"} and message.text == "":
            raise ValidationError("Message text must not be empty for user/bot messages.")
        if message.timestamp:
            parse_timestamp(message.timestamp)


def _response_times(messages: Sequence[ChatMessage]) -> Tuple[Optional[float], Optional[float]]:
    pairs: List[float] = []
    pending_user_time: Optional[_dt.datetime] = None
    for message in messages:
        ts = parse_timestamp(message.timestamp)
        if ts is None:
            continue
        if message.sender == "user":
            pending_user_time = ts
        elif message.sender == "bot" and pending_user_time is not None:
            diff = (ts - pending_user_time).total_seconds()
            if diff >= 0:
                pairs.append(diff)
            pending_user_time = None
    if not pairs:
        return None, None
    return pairs[0], round(statistics.mean(pairs), 3)


def _top_terms(text: str, limit: int = 12) -> Tuple[Tuple[str, int], ...]:
    stop = {
        "של", "על", "עם", "את", "זה", "זאת", "אני", "אתה", "אתם", "היא", "הוא",
        "לא", "כן", "יש", "אין", "the", "and", "for", "you", "are", "was", "were",
    }
    counts = Counter(t for t in tokenize(text) if len(t) > 1 and t not in stop)
    return tuple(counts.most_common(limit))


def _resolution_status(messages: Sequence[ChatMessage], sentiment: SentimentScore, escalation_requested: bool) -> Tuple[str, bool]:
    last_text = normalize_hebrew(messages[-1].text).lower() if messages else ""
    last_sender = messages[-1].sender if messages else "system"
    recent_text = " ".join(normalize_hebrew(m.text).lower() for m in messages[-3:])
    if any(term in recent_text for term in RESOLUTION_TERMS) and sentiment.label != "negative":
        return "resolved", False
    if last_sender == "user" and QUESTION_RE.search(last_text):
        return "open_question", True
    if escalation_requested:
        return "needs_human_review", True
    if sentiment.label == "negative":
        return "at_risk", True
    return "unclear", False


def _recommendations(
    analysis_basis: Mapping[str, Any],
    sentiment: SentimentScore,
    primary_intent: str,
    risk_flags: Mapping[str, int],
) -> Tuple[str, ...]:
    recs: List[str] = []
    if risk_flags:
        recs.append("Mask identifiers before exporting examples; retain only fields required for the analysis purpose.")
    if sentiment.label == "negative":
        recs.append("Review the final three turns and add a recovery response for angry or urgent customers.")
    if primary_intent == "billing_tax":
        recs.append("Route invoice, receipt, VAT, and refund questions to an approved finance workflow.")
    if primary_intent == "cancellation_refund":
        recs.append("Show the cancellation policy, transaction date, and refund channel before asking for more details.")
    if primary_intent == "appointment":
        recs.append("Offer two concrete appointment slots and confirm timezone and DD-MM-YYYY date format.")
    if primary_intent == "human_agent":
        recs.append("Escalate quickly; include a clear expected response time.")
    if analysis_basis.get("drop_off"):
        recs.append("Shorten the bot answer before the last user message and add one direct next action.")
    if not recs:
        recs.append("Sample this conversation during the next quality review and compare it with resolved conversations.")
    return tuple(dict.fromkeys(recs))


def _stable_session_id(messages: Sequence[Union[ChatMessage, Mapping[str, Any]]]) -> str:
    """Create a deterministic short session identifier from message content."""

    normalized = [asdict(_coerce_message(message)) for message in messages]
    payload = json.dumps(normalized, ensure_ascii=False, sort_keys=True, default=str)
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]
    return f"session-{digest}"


class ChatDataAnalyzerClient:
    """Synchronous Hebrew chat analyzer."""

    def __init__(self, custom_intents: Optional[Mapping[str, Sequence[str]]] = None) -> None:
        self.custom_intents = custom_intents or {}


    def create_conversation(
        self,
        messages: Sequence[Union[ChatMessage, Mapping[str, Any]]],
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Normalize one conversation and return a reusable create response."""

        validate_conversation(messages)
        resolved_session_id = session_id or _stable_session_id(messages)
        normalized_messages = [asdict(_coerce_message(message)) for message in messages]
        return {
            "session_id": resolved_session_id,
            "message_count": len(normalized_messages),
            "messages": normalized_messages,
        }

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze a single text snippet."""

        clean = normalize_hebrew(text)
        intents = classify_intent(clean, self.custom_intents)
        sentiment = sentiment_score(clean)
        risks = detect_sensitive_data(clean)
        return {
            "language": detect_language(clean),
            "sentiment": asdict(sentiment),
            "intents": [asdict(intent) for intent in intents],
            "risk_flags": risks,
            "top_terms": list(_top_terms(clean)),
            "anonymized_text": anonymize_text(clean) if risks else clean,
        }

    def analyze_conversation(
        self,
        messages: Sequence[Union[ChatMessage, Mapping[str, Any]]],
        session_id: str = "session",
    ) -> ConversationAnalysis:
        """Analyze one conversation."""

        validate_conversation(messages)
        coerced = [_coerce_message(m) for m in messages]
        all_text = " ".join(m.text for m in coerced if m.sender in {"user", "bot"})
        user_text = " ".join(m.text for m in coerced if m.sender == "user")
        intent_scores = classify_intent(user_text or all_text, self.custom_intents)
        primary_intent = intent_scores[0].intent
        sentiment = sentiment_score(all_text)
        risks = detect_sensitive_data(all_text)
        first_response, average_response = _response_times(coerced)
        escalation_requested = any(score.intent == "human_agent" and score.score > 0 for score in intent_scores)
        drop_off = coerced[-1].sender == "user" and len(coerced) >= 2
        status, unresolved = _resolution_status(coerced, sentiment, escalation_requested)
        question_count = sum(1 for m in coerced if m.sender == "user" and QUESTION_RE.search(normalize_hebrew(m.text)))
        base = {"drop_off": drop_off}
        recommendations = _recommendations(base, sentiment, primary_intent, risks)

        languages = Counter(detect_language(m.text) for m in coerced if m.text)
        language = languages.most_common(1)[0][0] if languages else "unknown"

        return ConversationAnalysis(
            session_id=session_id,
            language=language,
            primary_intent=primary_intent,
            intent_scores=intent_scores,
            sentiment=sentiment,
            risk_flags=risks,
            message_count=len(coerced),
            user_message_count=sum(1 for m in coerced if m.sender == "user"),
            bot_message_count=sum(1 for m in coerced if m.sender == "bot"),
            first_response_seconds=first_response,
            average_response_seconds=average_response,
            drop_off=drop_off,
            escalation_requested=escalation_requested,
            unresolved=unresolved,
            resolution_status=status,
            question_count=question_count,
            top_terms=_top_terms(all_text),
            recommendations=recommendations,
        )

    def analyze_dataset(self, conversations: Union[Sequence[Any], Mapping[str, Any]]) -> DatasetAnalysis:
        """Analyze many conversations.

        Accepted shapes:
        - [{"session_id": "...", "messages": [...]}, ...]
        - {"session-id": [...messages...], ...}
        - [...messages...] for a single conversation
        """

        normalized = normalize_dataset(conversations)
        analyses = tuple(
            self.analyze_conversation(item["messages"], session_id=item["session_id"])
            for item in normalized
        )
        if not analyses:
            raise ValidationError("Dataset must contain at least one conversation.")

        first_response_values = [a.first_response_seconds for a in analyses if a.first_response_seconds is not None]
        risk_totals: Counter[str] = Counter()
        for a in analyses:
            risk_totals.update(a.risk_flags)
        recommendations = dataset_recommendations(analyses)
        return DatasetAnalysis(
            conversation_count=len(analyses),
            total_messages=sum(a.message_count for a in analyses),
            language_distribution=dict(Counter(a.language for a in analyses)),
            sentiment_distribution=dict(Counter(a.sentiment.label for a in analyses)),
            intent_distribution=dict(Counter(a.primary_intent for a in analyses)),
            risk_flag_totals=dict(risk_totals),
            drop_off_rate=round(sum(a.drop_off for a in analyses) / len(analyses), 4),
            escalation_rate=round(sum(a.escalation_requested for a in analyses) / len(analyses), 4),
            unresolved_rate=round(sum(a.unresolved for a in analyses) / len(analyses), 4),
            average_first_response_seconds=round(statistics.mean(first_response_values), 3) if first_response_values else None,
            recommendations=recommendations,
            conversations=analyses,
        )

    def to_json(self, result: Union[ConversationAnalysis, DatasetAnalysis, Mapping[str, Any]], indent: int = 2) -> str:
        """Serialize analysis as JSON."""

        if hasattr(result, "__dataclass_fields__"):
            payload = asdict(result)  # type: ignore[arg-type]
        else:
            payload = dict(result)
        return json.dumps(payload, ensure_ascii=False, indent=indent, default=str)

    def to_csv(self, dataset: DatasetAnalysis) -> str:
        """Serialize conversation-level dataset results as CSV."""

        out = io.StringIO()
        writer = csv.DictWriter(
            out,
            fieldnames=[
                "session_id", "language", "primary_intent", "sentiment", "score",
                "message_count", "drop_off", "escalation_requested", "unresolved",
                "first_response_seconds", "average_response_seconds", "risk_flags",
            ],
        )
        writer.writeheader()
        for a in dataset.conversations:
            writer.writerow(
                {
                    "session_id": a.session_id,
                    "language": a.language,
                    "primary_intent": a.primary_intent,
                    "sentiment": a.sentiment.label,
                    "score": a.sentiment.score,
                    "message_count": a.message_count,
                    "drop_off": a.drop_off,
                    "escalation_requested": a.escalation_requested,
                    "unresolved": a.unresolved,
                    "first_response_seconds": a.first_response_seconds,
                    "average_response_seconds": a.average_response_seconds,
                    "risk_flags": json.dumps(a.risk_flags, ensure_ascii=False),
                }
            )
        return out.getvalue()


class AsyncChatDataAnalyzerClient:
    """Async wrapper around the synchronous analyzer."""

    def __init__(self, custom_intents: Optional[Mapping[str, Sequence[str]]] = None) -> None:
        self._sync = ChatDataAnalyzerClient(custom_intents=custom_intents)


    async def create_conversation(
        self,
        messages: Sequence[Union[ChatMessage, Mapping[str, Any]]],
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return await asyncio.to_thread(self._sync.create_conversation, messages, session_id)

    async def analyze_text(self, text: str) -> Dict[str, Any]:
        return await asyncio.to_thread(self._sync.analyze_text, text)

    async def analyze_conversation(
        self,
        messages: Sequence[Union[ChatMessage, Mapping[str, Any]]],
        session_id: str = "session",
    ) -> ConversationAnalysis:
        return await asyncio.to_thread(self._sync.analyze_conversation, messages, session_id)

    async def analyze_dataset(self, conversations: Union[Sequence[Any], Mapping[str, Any]]) -> DatasetAnalysis:
        return await asyncio.to_thread(self._sync.analyze_dataset, conversations)

    async def iter_analyze_jsonl(self, path: Union[str, Path]) -> AsyncIterator[ConversationAnalysis]:
        for item in load_jsonl(path):
            yield await self.analyze_conversation(item["messages"], item.get("session_id", "session"))


def normalize_dataset(conversations: Union[Sequence[Any], Mapping[str, Any]]) -> List[Dict[str, Any]]:
    """Normalize accepted dataset shapes."""

    if isinstance(conversations, Mapping):
        if "messages" in conversations:
            return [{"session_id": str(conversations.get("session_id", "session-1")), "messages": conversations["messages"]}]
        return [{"session_id": str(k), "messages": v} for k, v in conversations.items()]
    if not isinstance(conversations, Sequence) or isinstance(conversations, (str, bytes)):
        raise ValidationError("Dataset must be a sequence or mapping.")
    if not conversations:
        raise ValidationError("Dataset must not be empty.")
    first = conversations[0]
    if isinstance(first, Mapping) and "messages" in first:
        return [
            {"session_id": str(item.get("session_id", f"session-{i+1}")), "messages": item["messages"]}
            for i, item in enumerate(conversations)
        ]
    return [{"session_id": "session-1", "messages": conversations}]


def load_json(path: Union[str, Path]) -> Any:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_jsonl(path: Union[str, Path]) -> Iterator[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as fh:
        for i, line in enumerate(fh, start=1):
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if "messages" not in payload:
                raise ValidationError(f"JSONL line {i} must contain messages.")
            payload.setdefault("session_id", f"line-{i}")
            yield payload


def load_csv(path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Load a flat CSV with session_id, sender, text, timestamp columns."""

    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    with open(path, "r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        required = {"session_id", "sender", "text"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValidationError(f"CSV missing columns: {', '.join(sorted(missing))}")
        for row in reader:
            sid = row.get("session_id") or "session"
            grouped[sid].append(
                {
                    "sender": row.get("sender"),
                    "text": row.get("text"),
                    "timestamp": row.get("timestamp") or row.get("created_at") or None,
                }
            )
    return [{"session_id": sid, "messages": messages} for sid, messages in grouped.items()]


def load_any(path: Union[str, Path]) -> Any:
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix == ".json":
        return load_json(p)
    if suffix == ".jsonl":
        return list(load_jsonl(p))
    if suffix == ".csv":
        return load_csv(p)
    raise ValidationError("Supported input files: .json, .jsonl, .csv")


def dataset_recommendations(analyses: Sequence[ConversationAnalysis]) -> Tuple[str, ...]:
    recs: List[str] = []
    total = len(analyses)
    if total == 0:
        return ()
    drop_rate = sum(a.drop_off for a in analyses) / total
    unresolved_rate = sum(a.unresolved for a in analyses) / total
    negative_rate = sum(a.sentiment.label == "negative" for a in analyses) / total
    escalation_rate = sum(a.escalation_requested for a in analyses) / total
    if drop_rate >= 0.25:
        recs.append("Investigate drop-off clusters by channel and shorten high-friction bot messages.")
    if unresolved_rate >= 0.2:
        recs.append("Create a weekly unresolved-chat review and assign each recurring intent to one owner.")
    if negative_rate >= 0.15:
        recs.append("Add complaint recovery templates and track response time for negative conversations.")
    if escalation_rate >= 0.1:
        recs.append("Tune intent routing so human-agent requests bypass unnecessary bot questions.")
    top_intent = Counter(a.primary_intent for a in analyses).most_common(1)[0][0]
    recs.append(f"Review the top intent '{top_intent}' first; improvements there affect the largest share of chats.")
    return tuple(dict.fromkeys(recs))


def write_sample_dataset(path: Union[str, Path]) -> Path:
    """Write a runnable Hebrew sample dataset."""

    sample = [
        {
            "session_id": "demo-001",
            "messages": [
                {"sender": "user", "text": "שלום, אפשר לקבל חשבונית מס על 350 ₪?", "timestamp": "2026-03-01T09:00:00"},
                {"sender": "bot", "text": "כן. נא לשלוח מספר עוסק או ח.פ.", "timestamp": "2026-03-01T09:00:07"},
                {"sender": "user", "text": "תודה רבה, הסתדר.", "timestamp": "2026-03-01T09:01:00"},
            ],
        },
        {
            "session_id": "demo-002",
            "messages": [
                {"sender": "user", "text": "המשלוח לא הגיע ואני מחכה כבר שבוע. רוצה נציג עכשיו.", "timestamp": "2026-03-02T18:20:00"},
                {"sender": "bot", "text": "אפשר לבדוק לפי מספר הזמנה.", "timestamp": "2026-03-02T18:22:30"},
            ],
        },
    ]
    p = Path(path)
    p.write_text(json.dumps(sample, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


__all__ = [
    "AsyncChatDataAnalyzerClient",
    "ChatDataAnalyzerClient",
    "ChatMessage",
    "ConversationAnalysis",
    "DatasetAnalysis",
    "IntentScore",
    "SentimentScore",
    "ValidationError",
    "anonymize_text",
    "classify_intent",
    "detect_language",
    "detect_sensitive_data",
    "load_any",
    "load_csv",
    "load_json",
    "load_jsonl",
    "normalize_dataset",
    "normalize_hebrew",
    "parse_timestamp",
    "sentiment_score",
    "tokenize",
    "validate_conversation",
    "write_sample_dataset",
]
