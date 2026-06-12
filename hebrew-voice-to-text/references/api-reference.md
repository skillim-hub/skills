# API and Regulation Reference

## Scope

This skill is provider-neutral. It does not call a hosted transcription service directly. It prepares local jobs, validates provider command output, normalizes Hebrew text, exports files, and helps detect sensitive values. Connect it to a chosen transcription provider through a command that prints JSON.

Use the examples below as the stable local contract between the skill and any external provider.

## Local command contract

### Environment variables

| Variable | Purpose | Example |
|---|---|---|
| `HVTT_ENV` | Environment label | `sandbox` or `production` |
| `HVTT_PROVIDER_COMMAND` | Command that prints provider JSON | `python provider.py {input} {language}` |
| `HVTT_LANGUAGE` | Language code | `he-IL` |
| `HVTT_INPUT_FOLDER` | Example batch folder | `./audio` |
| `HVTT_JOBS_DIR` | Local job folder | `.hvt-jobs` |

### Placeholders

| Placeholder | Replaced with |
|---|---|
| `{input}` | Source file path |
| `{language}` | Language code, usually `he-IL` |
| `{lang}` | Alias for language |
| `{env}` | `sandbox` or `production` |

### Provider stdout response

```json
{
  "language": "he-IL",
  "duration_seconds": 38.2,
  "segments": [
    {
      "start": 0.0,
      "end": 4.1,
      "speaker": "לקוח",
      "text": "שלום, אני רוצה לברר על חשבונית מספר 123.",
      "confidence": 0.91
    },
    {
      "start": 4.1,
      "end": 8.7,
      "speaker": "נציג",
      "text": "כן, החשבונית על סך ₪450 נשלחה ב-15/03/2026.",
      "confidence": 0.89
    }
  ],
  "warnings": ["background_noise"]
}
```

### Minimal provider response

```json
{
  "language": "he-IL",
  "text": "שלום, רציתי לבדוק הזמנה."
}
```

The parser converts a `text` response into one segment with `דובר 1`.

## Local job create response

```json
{
  "id": "hvt_8f0a7c812345abcd",
  "env": "sandbox",
  "job_file": ".hvt-jobs/hvt_8f0a7c812345abcd.json",
  "next": "show-job hvt_8f0a7c812345abcd --jobs-dir .hvt-jobs"
}
```

Use the `id` in the next command:

```bash
CREATE_RESPONSE=$(hebrew-voice-to-text --env sandbox create-job sample.txt --jobs-dir .hvt-jobs)
JOB_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")
hebrew-voice-to-text --env sandbox show-job "$JOB_ID" --jobs-dir .hvt-jobs
```

## Provider-neutral request body

```json
{
  "id": "hvt_8f0a7c812345abcd",
  "input": {
    "file": "sample.wav",
    "language": "he-IL"
  },
  "options": {
    "punctuation": true,
    "speaker_labels": true,
    "expected_speakers": 2,
    "timestamps": true,
    "sensitivity": "medium"
  },
  "outputs": ["txt", "json", "srt"],
  "environment": "sandbox"
}
```

## Error table

| Code | Condition | Response |
|---|---|---|
| `file_not_found` | Source or job file does not exist | Stop and correct the path. |
| `provider_missing` | Audio input has no provider command | Configure `HVTT_PROVIDER_COMMAND` or pass `--provider-command`. |
| `provider_failed` | Provider command exits non-zero | Capture stderr, keep source audio, retry after fixing provider. |
| `invalid_json` | Provider stdout is not valid JSON | Require UTF-8 JSON with `segments` or `text`. |
| `missing_segments` | Provider response lacks `segments` and `text` | Reject response. |
| `unsupported_export` | Format is not TXT, JSON, SRT, VTT, or Markdown | Select supported output format. |
| `consent_required` | Medium or high sensitivity without consent or lawful basis | Stop processing until approved. |
| `env_invalid` | Environment is neither sandbox nor production | Use the accepted values only. |

## Israeli regulatory references

This section is not legal advice. Verify obligations for each business process and provider.

| Reference | Practical implication for transcription |
|---|---|
| Protection of Privacy Law, 5741-1981 | Treat identifiable voice, transcript text, phone numbers, and customer details as personal information when applicable. |
| Protection of Privacy Regulations, Data Security, 5777-2017 | Apply access control, retention limits, backups, incident handling, and supplier controls according to database sensitivity. |
| Privacy Protection Authority guidance | Use data minimization, purpose limitation, transparency, and documented processing practices. |
| Wiretap Law, 5739-1979 | Check call recording legality, consent, and participant notification before processing calls. |
| Computers Law, 5755-1995 | Protect systems, files, credentials, and automated processing from unauthorized access or disruption. |
| Consumer Protection Law, 5741-1981 | Preserve customer commitments, cancellation requests, prices, and delivery details accurately when used for consumer service. |
| Electronic Signature Law, 5761-2001 | Do not treat a transcript as a signed document unless the required signature process exists separately. |
| Accessibility regulations for service providers | Use captions and readable transcripts where required by the service context. |


## Web-validated official source notes

Validated on 03/06/2026. Keep this section provider-neutral; it records checks that affect Israeli small-business transcription workflows. Full source details are in `references/verification-log.md`.

| Topic | Confirmed handling |
|---|---|
| VAT in transcripted invoices | Current validated rate is 18% from 01/01/2025. Do not calculate tax automatically from speech unless the business process explicitly asks for it and current official rates are rechecked. |
| WhatsApp voice audio | For official Business Platform voice-message flows, prefer OGG audio encoded with OPUS. Keep inbound originals unchanged before conversion. |
| WhatsApp audio webhook | Treat inbound audio as a `messages` webhook with `type: audio` and audio metadata. The local package does not expose webhook endpoints. |
| Provider endpoints | The package has no hosted API host or remote endpoint path. Integrate external providers through `HVTT_PROVIDER_COMMAND` and the JSON contract above. |
| Privacy terminology | Use `בעל שליטה במאגר מידע`, `מחזיק`, `מנהל מאגר`, `מידע אישי`, and `מידע בעל רגישות מיוחדת` in Hebrew compliance notes. |
| Incident reporting | For serious information-security incidents, record enough details to complete the official Privacy Protection Authority form when required. |
| Accessibility | Captions or text transcripts may be required by the service context. Confirm applicability before publishing video or training material. |

## Data classification

| Sensitivity | Examples | Minimum handling |
|---|---|---|
| Low | Public product question, store hours | Basic retention and review. |
| Medium | Order details, address, phone number, invoice amount | Consent or lawful basis, redaction before external sharing, controlled access. |
| High | Health, financial hardship, child voice, identity number, payment details | Strict minimization, documented basis, approved provider, short retention, manual review. |

## Request and response examples

### Text input

```bash
hebrew-voice-to-text transcribe sample.txt --output-dir out --format json
```

Response:

```json
{
  "written": ["out/sample.json"],
  "summary": {
    "job_id": null,
    "language": "he-IL",
    "segments": 1,
    "word_count": 7,
    "duration_seconds": null,
    "sensitive_terms": ["amount"],
    "warnings": []
  }
}
```

### Audio input with provider command

```bash
hebrew-voice-to-text --env production transcribe call.wav \
  --provider-command "python provider.py {input} {language}" \
  --output-dir out --format txt --format json --format srt
```

Response:

```json
{
  "written": ["out/call.txt", "out/call.json", "out/call.srt"],
  "summary": {
    "job_id": null,
    "language": "he-IL",
    "segments": 12,
    "word_count": 184,
    "duration_seconds": 92.3,
    "sensitive_terms": ["phone", "amount"],
    "warnings": []
  }
}
```

## Provider evaluation checklist

- Confirm Hebrew `he-IL` support.
- Confirm punctuation support.
- Confirm speaker labels or channel separation.
- Confirm timestamp output.
- Confirm UTF-8 JSON output.
- Confirm retention settings and deletion path.
- Confirm location and access to stored audio.
- Confirm subcontractor use.
- Confirm incident notification process.
- Confirm that test data in sandbox is not used for unrelated purposes.

## Export formats

| Format | Best use | Notes |
|---|---|---|
| TXT | Customer notes and follow-up | Easy to paste into service systems. |
| JSON | Automation, auditing, provider comparison | Keeps segments, speakers, confidence, warnings. |
| SRT | Video captions | Uses comma milliseconds. |
| VTT | Web captions | Uses dot milliseconds and `WEBVTT` header. |
| Markdown | Review documents | Keeps summary and segment list. |
