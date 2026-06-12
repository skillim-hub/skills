from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

import chat_data_analyzer_client as client


def sample_messages():
    return [
        {"sender": "user", "text": "שלום, אפשר לקבל חשבונית מס על 350 ₪?", "timestamp": "2026-03-01T09:00:00"},
        {"sender": "bot", "text": "כן. נא לשלוח מספר עוסק.", "timestamp": "2026-03-01T09:00:10"},
        {"sender": "user", "text": "תודה רבה, הסתדר.", "timestamp": "2026-03-01T09:01:00"},
    ]


def test_normalize_strips_niqqud():
    assert client.normalize_hebrew("שָׁלוֹם\u200f") == "שלום"


def test_detect_language_hebrew():
    assert client.detect_language("שלום, אפשר לקבל קבלה?") == "he"


def test_detect_language_english():
    assert client.detect_language("hello can I get a receipt") == "en"


def test_detect_language_mixed():
    assert client.detect_language("שלום invoice please") == "mixed"


def test_tokenize_hebrew_and_number():
    assert "חשבונית" in client.tokenize("חשבונית 350 ₪")


def test_sentiment_positive():
    result = client.sentiment_score("תודה רבה, שירות מעולה")
    assert result.label == "positive"
    assert result.score > 0


def test_sentiment_negative():
    result = client.sentiment_score("השירות גרוע ויש תקלה דחוף")
    assert result.label == "negative"
    assert result.score < 0


def test_sentiment_negation_of_positive():
    result = client.sentiment_score("זה לא טוב בכלל")
    assert result.label == "negative"


def test_sentiment_negated_negative_softens():
    result = client.sentiment_score("לא גרוע, תודה")
    assert result.score >= 0


def test_intent_billing_tax():
    scores = client.classify_intent("צריך חשבונית מס וקבלה")
    assert scores[0].intent == "billing_tax"


def test_intent_appointment():
    scores = client.classify_intent("אפשר לקבוע תור ליום שני?")
    assert scores[0].intent == "appointment"


def test_intent_human_agent():
    scores = client.classify_intent("רוצה לדבר עם נציג")
    assert scores[0].intent == "human_agent"


def test_custom_intent():
    scores = client.classify_intent("יש בעיה במנוי הפרימיום", {"subscription": ["מנוי", "פרימיום"]})
    assert scores[0].intent == "subscription"


def test_detect_sensitive_email_phone():
    flags = client.detect_sensitive_data("המייל test@example.com והטלפון 050-123-4567")
    assert flags["email"] == 1
    assert flags["phone"] == 1


def test_detect_sensitive_israeli_id():
    flags = client.detect_sensitive_data("מספר זהות 123456782")
    assert flags["israeli_id_like"] == 1


def test_anonymize_masks_identifiers():
    masked = client.anonymize_text("test@example.com 0501234567 123456782")
    assert "[EMAIL]" in masked
    assert "[PHONE]" in masked
    assert "[ISRAELI_ID]" in masked


def test_validate_rejects_empty_conversation():
    with pytest.raises(client.ValidationError):
        client.validate_conversation([])


def test_parse_dd_mm_yyyy_timestamp():
    parsed = client.parse_timestamp("03-06-2026 14:05:00")
    assert parsed.year == 2026
    assert parsed.day == 3


def test_analyze_conversation_primary_intent():
    analyzer = client.ChatDataAnalyzerClient()
    result = analyzer.analyze_conversation(sample_messages(), "s1")
    assert result.primary_intent == "billing_tax"
    assert result.message_count == 3


def test_analyze_conversation_response_times():
    analyzer = client.ChatDataAnalyzerClient()
    result = analyzer.analyze_conversation(sample_messages(), "s1")
    assert result.first_response_seconds == 10
    assert result.average_response_seconds == 10


def test_analyze_conversation_resolved():
    analyzer = client.ChatDataAnalyzerClient()
    result = analyzer.analyze_conversation(sample_messages(), "s1")
    assert result.resolution_status == "resolved"
    assert result.unresolved is False


def test_drop_off_open_question():
    analyzer = client.ChatDataAnalyzerClient()
    result = analyzer.analyze_conversation([
        {"sender": "bot", "text": "שלום"},
        {"sender": "user", "text": "כמה עולה משלוח?"},
    ], "s2")
    assert result.drop_off is True
    assert result.unresolved is True


def test_dataset_aggregate_counts():
    analyzer = client.ChatDataAnalyzerClient()
    dataset = analyzer.analyze_dataset([
        {"session_id": "s1", "messages": sample_messages()},
        {"session_id": "s2", "messages": [
            {"sender": "user", "text": "המשלוח לא הגיע, רוצה נציג"},
            {"sender": "bot", "text": "אפשר לבדוק"},
        ]},
    ])
    assert dataset.conversation_count == 2
    assert dataset.total_messages == 5


def test_dataset_distributions():
    analyzer = client.ChatDataAnalyzerClient()
    dataset = analyzer.analyze_dataset({"s1": sample_messages()})
    assert dataset.intent_distribution["billing_tax"] == 1
    assert sum(dataset.sentiment_distribution.values()) == 1


def test_to_json_contains_hebrew():
    analyzer = client.ChatDataAnalyzerClient()
    result = analyzer.analyze_conversation(sample_messages(), "s1")
    text = analyzer.to_json(result)
    assert "billing_tax" in text
    assert "\\u05" not in text


def test_to_csv_header():
    analyzer = client.ChatDataAnalyzerClient()
    dataset = analyzer.analyze_dataset({"s1": sample_messages()})
    csv_text = analyzer.to_csv(dataset)
    assert "session_id,language,primary_intent" in csv_text


def test_load_jsonl(tmp_path):
    path = tmp_path / "data.jsonl"
    path.write_text(json.dumps({"session_id": "s1", "messages": sample_messages()}, ensure_ascii=False) + "\n", encoding="utf-8")
    loaded = list(client.load_jsonl(path))
    assert loaded[0]["session_id"] == "s1"


def test_load_csv(tmp_path):
    path = tmp_path / "data.csv"
    path.write_text("session_id,sender,text,timestamp\ns1,user,שלום,\ns1,bot,שלום רב,\n", encoding="utf-8")
    loaded = client.load_csv(path)
    assert loaded[0]["session_id"] == "s1"
    assert len(loaded[0]["messages"]) == 2


def test_write_sample_dataset(tmp_path):
    path = client.write_sample_dataset(tmp_path / "sample.json")
    assert path.exists()
    assert "חשבונית" in path.read_text(encoding="utf-8")


def test_async_client_text():
    async def run():
        analyzer = client.AsyncChatDataAnalyzerClient()
        result = await analyzer.analyze_text("שלום, יש תקלה דחוף")
        return result
    result = asyncio.run(run())
    assert result["sentiment"]["label"] == "negative"


def test_async_client_dataset():
    async def run():
        analyzer = client.AsyncChatDataAnalyzerClient()
        return await analyzer.analyze_dataset({"s1": sample_messages()})
    dataset = asyncio.run(run())
    assert dataset.conversation_count == 1


def test_normalize_dataset_single_conversation():
    normalized = client.normalize_dataset(sample_messages())
    assert normalized[0]["session_id"] == "session-1"


def test_risk_flags_do_not_count_invalid_id():
    flags = client.detect_sensitive_data("מספר 111111111 לא בהכרח תז")
    assert "israeli_id_like" not in flags



def test_create_conversation_response_chains_session_id():
    analyzer = client.ChatDataAnalyzerClient()
    created = analyzer.create_conversation(sample_messages())
    result = analyzer.analyze_conversation(created["messages"], session_id=created["session_id"])
    assert result.session_id == created["session_id"]
    assert created["message_count"] == 3


def test_importable_module_exposes_public_client():
    from chat_data_analyzer_client import ChatDataAnalyzerClient
    assert ChatDataAnalyzerClient.__name__ == "ChatDataAnalyzerClient"
