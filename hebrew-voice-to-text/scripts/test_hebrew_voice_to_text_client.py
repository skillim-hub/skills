from __future__ import annotations

import asyncio
import json
import subprocess
import sys
import wave
from pathlib import Path

import pytest

from hebrew_voice_to_text import (
    HebrewVoiceTextClient,
    JobSpec,
    ProviderCommandError,
    TranscriptionResult,
    TranscriptionSegment,
    build_job_id,
    format_timestamp,
    render_markdown,
    render_srt,
    render_vtt,
    validate_consent,
    validate_env,
)

ROOT = Path(__file__).resolve().parents[1]
CLI_MODULE = "hebrew_voice_to_text.cli"


def make_wav(path: Path, seconds: float = 0.1, rate: int = 8000) -> None:
    frames = int(seconds * rate)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(rate)
        wav_file.writeframes(b"\x00\x00" * frames)


def test_normalize_removes_niqqud_and_collapses_spaces() -> None:
    client = HebrewVoiceTextClient()
    assert client.normalize_hebrew_text("שָׁלוֹם   עולם") == "שלום עולם."


def test_normalize_removes_rtl_marks() -> None:
    client = HebrewVoiceTextClient()
    assert client.normalize_hebrew_text("\u200fשלום") == "שלום."


def test_normalize_keeps_existing_question_mark() -> None:
    client = HebrewVoiceTextClient()
    assert client.normalize_hebrew_text("מה הסטטוס?") == "מה הסטטוס?"


def test_light_punctuation_detects_question_cue() -> None:
    client = HebrewVoiceTextClient()
    assert client.add_light_punctuation("מה מספר ההזמנה") == "מה מספר ההזמנה?"


def test_detect_phone_number() -> None:
    client = HebrewVoiceTextClient()
    assert "phone" in client.detect_sensitive_terms("תחזרו אליי ל-052-1234567")


def test_detect_israeli_id_like_value() -> None:
    client = HebrewVoiceTextClient()
    assert "israeli_id" in client.detect_sensitive_terms("תעודת זהות 123456789")


def test_detect_credit_card_like_value() -> None:
    client = HebrewVoiceTextClient()
    assert "payment_card" in client.detect_sensitive_terms("4111 1111 1111 1111")


def test_detect_bank_hint() -> None:
    client = HebrewVoiceTextClient()
    assert "banking" in client.detect_sensitive_terms("מספר חשבון בנק נשלח בהודעה")


def test_detect_amount() -> None:
    client = HebrewVoiceTextClient()
    assert "amount" in client.detect_sensitive_terms("הסכום הוא ₪1,280")


def test_redact_phone_number() -> None:
    client = HebrewVoiceTextClient()
    assert "052-***4567" in client.redact_sensitive_text("052-1234567")


def test_redact_id_number() -> None:
    client = HebrewVoiceTextClient()
    assert "********9" in client.redact_sensitive_text("123456789")


def test_label_segments_cycles_speakers() -> None:
    client = HebrewVoiceTextClient()
    segments = client.label_segments(["שלום", "היי"], ["דובר 1", "דובר 2"])
    assert [s.speaker for s in segments] == ["דובר 1", "דובר 2"]


def test_parse_provider_payload_text_only() -> None:
    client = HebrewVoiceTextClient()
    result = client.parse_provider_payload({"text": "שלום"})
    assert result.segments[0].text == "שלום."


def test_parse_provider_payload_requires_segments_or_text() -> None:
    client = HebrewVoiceTextClient()
    with pytest.raises(ProviderCommandError):
        client.parse_provider_payload({"language": "he-IL"})


def test_result_word_count() -> None:
    result = TranscriptionResult("he-IL", [TranscriptionSegment(0, 1, "דובר 1", "שלום עולם")])
    assert result.word_count == 2


def test_format_timestamp_srt() -> None:
    assert format_timestamp(65.432) == "00:01:05,432"


def test_format_timestamp_vtt() -> None:
    assert format_timestamp(65.432, vtt=True) == "00:01:05.432"


def test_render_srt() -> None:
    result = TranscriptionResult("he-IL", [TranscriptionSegment(0, 1.5, "דובר 1", "שלום.")])
    srt = render_srt(result)
    assert "1\n00:00:00,000 --> 00:00:01,500" in srt
    assert "דובר 1: שלום." in srt


def test_render_vtt_starts_with_header() -> None:
    result = TranscriptionResult("he-IL", [TranscriptionSegment(0, 1, "דובר 1", "שלום.")])
    assert render_vtt(result).startswith("WEBVTT")


def test_render_markdown_contains_sensitive_terms() -> None:
    result = TranscriptionResult("he-IL", [], sensitive_terms=["phone"])
    assert "phone" in render_markdown(result)


def test_inspect_wav(tmp_path: Path) -> None:
    wav_path = tmp_path / "sample.wav"
    make_wav(wav_path)
    info = HebrewVoiceTextClient().inspect_audio(wav_path)
    assert info.is_wav
    assert info.is_supported_audio
    assert info.channels == 1
    assert info.sample_rate_hz == 8000
    assert info.duration_seconds == pytest.approx(0.1)


def test_inspect_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        HebrewVoiceTextClient().inspect_audio(tmp_path / "missing.wav")


def test_transcribe_txt_file(tmp_path: Path) -> None:
    txt = tmp_path / "note.txt"
    txt.write_text("שלום   עולם", encoding="utf-8")
    result = HebrewVoiceTextClient().transcribe(txt)
    assert result.text == "דובר 1: שלום עולם."


def test_transcribe_json_file(tmp_path: Path) -> None:
    payload = {"language": "he-IL", "segments": [{"start": 0, "end": 1, "text": "שלום"}]}
    path = tmp_path / "provider.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    result = HebrewVoiceTextClient().transcribe(path)
    assert result.segments[0].speaker == "דובר 1"


def test_transcribe_audio_without_provider_raises(tmp_path: Path) -> None:
    wav_path = tmp_path / "sample.wav"
    make_wav(wav_path)
    with pytest.raises(ProviderCommandError):
        HebrewVoiceTextClient().transcribe(wav_path)


def test_transcribe_with_provider_command(tmp_path: Path) -> None:
    wav_path = tmp_path / "sample.wav"
    make_wav(wav_path)
    provider = tmp_path / "provider.py"
    provider.write_text(
        "import json, sys\n"
        "print(json.dumps({'language': sys.argv[2], 'segments': [{'start': 0, 'end': 1, 'speaker': 'לקוח', 'text': 'שלום'}]}, ensure_ascii=False))\n",
        encoding="utf-8",
    )
    command = [sys.executable, str(provider), "{input}", "{language}"]
    result = HebrewVoiceTextClient(provider_command=command).transcribe(wav_path)
    assert result.language == "he-IL"
    assert result.segments[0].speaker == "לקוח"


@pytest.mark.asyncio
async def test_async_transcribe_txt(tmp_path: Path) -> None:
    txt = tmp_path / "note.txt"
    txt.write_text("שלום", encoding="utf-8")
    result = await HebrewVoiceTextClient().async_transcribe(txt)
    assert "שלום" in result.text


def test_save_result_writes_formats(tmp_path: Path) -> None:
    result = TranscriptionResult("he-IL", [TranscriptionSegment(0, 1, "דובר 1", "שלום.")], source_path="x.wav")
    paths = HebrewVoiceTextClient().save_result(result, tmp_path, formats=("txt", "json", "srt", "vtt", "md"))
    assert {p.suffix for p in paths} == {".txt", ".json", ".srt", ".vtt", ".md"}


def test_save_result_rejects_unknown_format(tmp_path: Path) -> None:
    result = TranscriptionResult("he-IL", [])
    with pytest.raises(ValueError):
        HebrewVoiceTextClient().save_result(result, tmp_path, formats=("docx",))


def test_validate_consent_blocks_medium_without_consent() -> None:
    with pytest.raises(PermissionError):
        validate_consent(False, "medium")


def test_validate_consent_allows_low_without_consent() -> None:
    validate_consent(False, "low")


def test_validate_env_rejects_unknown() -> None:
    with pytest.raises(ValueError):
        validate_env("qa")


def test_build_job_id_is_stable(tmp_path: Path) -> None:
    txt = tmp_path / "note.txt"
    txt.write_text("שלום", encoding="utf-8")
    assert build_job_id(txt) == build_job_id(txt)


def test_create_write_load_job(tmp_path: Path) -> None:
    txt = tmp_path / "note.txt"
    txt.write_text("שלום", encoding="utf-8")
    client = HebrewVoiceTextClient(env="sandbox")
    job = client.create_job(txt, expected_speakers=2, outputs=("txt", "json"), jobs_dir=tmp_path / "jobs")
    loaded = client.load_job(job.id, tmp_path / "jobs")
    assert loaded.expected_speakers == 2
    assert loaded.env == "sandbox"


def test_provider_request_contains_options(tmp_path: Path) -> None:
    txt = tmp_path / "note.txt"
    txt.write_text("שלום", encoding="utf-8")
    client = HebrewVoiceTextClient()
    job = client.create_job(txt, expected_speakers=2)
    request = client.build_provider_request(job)
    assert request["options"]["speaker_labels"] is True
    assert request["options"]["expected_speakers"] == 2


def test_job_spec_roundtrip() -> None:
    job = JobSpec(id="hvt_1", source_file="x.wav", outputs=["txt"])
    assert JobSpec.from_dict(job.to_dict()).id == "hvt_1"


def test_summary_counts_segments() -> None:
    client = HebrewVoiceTextClient()
    result = TranscriptionResult("he-IL", [TranscriptionSegment(0, 1, "דובר 1", "שלום")])
    assert client.summarize_result(result)["segments"] == 1


def test_cli_normalize_command() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", CLI_MODULE, "normalize", "שלום   עולם"],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert completed.stdout.strip() == "שלום עולם."


def test_cli_create_and_show_job_chain(tmp_path: Path) -> None:
    txt = tmp_path / "note.txt"
    txt.write_text("שלום", encoding="utf-8")
    jobs_dir = tmp_path / "jobs"
    created = subprocess.run(
        [sys.executable, "-m", CLI_MODULE, "--env", "sandbox", "create-job", str(txt), "--jobs-dir", str(jobs_dir), "--expected-speakers", "2"],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    create_data = json.loads(created.stdout)
    shown = subprocess.run(
        [sys.executable, "-m", CLI_MODULE, "--env", "sandbox", "show-job", create_data["id"], "--jobs-dir", str(jobs_dir)],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    show_data = json.loads(shown.stdout)
    assert show_data["id"] == create_data["id"]
    assert show_data["options"]["expected_speakers"] == 2


def test_cli_transcribe_outputs_json_summary(tmp_path: Path) -> None:
    txt = tmp_path / "note.txt"
    txt.write_text("שלום", encoding="utf-8")
    out = tmp_path / "out"
    completed = subprocess.run(
        [sys.executable, "-m", CLI_MODULE, "transcribe", str(txt), "--output-dir", str(out), "--format", "json"],
        check=True,
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    data = json.loads(completed.stdout)
    assert data["summary"]["word_count"] == 1
    assert (out / "note.json").exists()
