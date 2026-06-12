# Voice-to-Text in Hebrew

Transcribe Hebrew audio messages and calls into readable text with punctuation, timestamps, speaker labels, privacy checks, and export files. Use the package for WhatsApp voice notes, call recordings, customer follow-ups, subtitles, meeting summaries, and local provider automation.

## Install

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
pip install -r requirements-dev.txt
```

## Quick start

Normalize text:

```bash
hebrew-voice-to-text normalize "שלום   אני רוצה לבדוק חשבונית"
```

Create a local transcription job, extract the job id from the create response, then use it in the next step:

```bash
printf "שלום, שלחתי חשבונית על ₪450 ל-15/03/2026" > sample.txt

CREATE_RESPONSE=$(hebrew-voice-to-text --env sandbox create-job sample.txt --jobs-dir .hvt-jobs)
JOB_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")

hebrew-voice-to-text --env sandbox show-job "$JOB_ID" --jobs-dir .hvt-jobs
hebrew-voice-to-text --env sandbox run-job "$JOB_ID" --jobs-dir .hvt-jobs --output-dir out
```

Run a provider command that emits JSON:

```bash
export HVTT_PROVIDER_COMMAND='python provider.py {input} {language}'
hebrew-voice-to-text --env sandbox transcribe sample.wav \
  --output-dir out --format txt --format json --format srt --format vtt
```

Provider stdout contract:

```json
{
  "language": "he-IL",
  "duration_seconds": 3.4,
  "segments": [
    {
      "start": 0.0,
      "end": 3.4,
      "speaker": "דובר 1",
      "text": "שלום, אני רוצה לבדוק הזמנה.",
      "confidence": 0.88
    }
  ]
}
```

Use the Python package:

```python
from hebrew_voice_to_text import HebrewVoiceTextClient

client = HebrewVoiceTextClient(env="sandbox")
result = client.transcribe("sample.txt")
print(result.text)
```

Run tests and syntax checks:

```bash
pytest
python -m compileall scripts/ -q
```

## File index

| Path | Purpose |
|---|---|
| `SKILL.md` | English operating guide, examples, decision trees, edge cases, anti-patterns, and production checklist. |
| `SKILL_HE.md` | Hebrew guide with Israeli terminology, ₪, and DD/MM/YYYY date examples. |
| `references/api-reference.md` | Provider-neutral API contract, Israeli regulatory notes, request and response examples, error tables. |
| `references/workflow-guide.md` | End-to-end workflows for WhatsApp, calls, accounting, CRM, subtitles, and batch processing. |
| `references/troubleshooting.md` | Audio, Hebrew, speaker, provider, export, and privacy troubleshooting. |
| `references/test-scenarios.md` | More than 20 concrete scenarios and acceptance criteria. |
| `references/migration-checklist.md` | Migration plan from ad-hoc transcription to a controlled process. |
| `references/branding-audit.md` | Verification report for neutral packaging constraints. |
| `references/hebrew-qa-log.md` | Hebrew terminology and localization correction log. |
| `references/verification-log.md` | Web validation log with Pass 1 and Pass 2 source checks. |
| `hebrew_voice_to_text/` | Installable Python package. |
| `scripts/hebrew_voice_to_text_client.py` | Underscored typed helper module for script-oriented use. |
| `scripts/hebrew-voice-to-text-cli.py` | Click-based command line interface. |
| `scripts/examples/` | Runnable examples that read environment variables and accept `--env sandbox|production`. |

## Production reminders

Confirm consent or another lawful basis before processing voice recordings. Use `he-IL`. Use speaker labels or channel labels for multi-speaker calls. Mark uncertainty instead of guessing. Redact phone numbers, identity numbers, payment details, bank hints, and amounts before sharing. Review names, amounts, dates, addresses, commitments, and cancellation requests manually. Keep source audio unchanged until transcript quality is accepted.
