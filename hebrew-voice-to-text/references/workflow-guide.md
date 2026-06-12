# Workflow Guide

## Workflow 1: WhatsApp voice note to customer follow-up

### Goal

Convert a short Hebrew voice note into a readable customer follow-up while protecting private details.

### Steps

1. Save the original voice note without modification.
2. Create a local job in the sandbox environment:

```bash
hebrew-voice-to-text --env sandbox create-job whatsapp.opus --jobs-dir .hvt-jobs --expected-speakers 1
```

3. Extract the job id from the response.
4. Run the job with an approved provider command.
5. Export TXT and JSON.
6. Review names, phone numbers, dates, amounts, and promised actions.
7. Redact sensitive values before sending a summary outside the business.
8. Store the accepted transcript and delete temporary working copies according to policy.

### Acceptance criteria

- Transcript uses natural Hebrew.
- Speaker label is stable.
- Amounts use `₪`.
- Dates use `DD/MM/YYYY`.
- Sensitive values are detected before sharing.

## Workflow 2: Recorded customer call to service record

### Goal

Turn a call into a structured record for support, delivery, or cancellation handling.

### Steps

1. Confirm call recording consent or another lawful basis.
2. Classify sensitivity.
3. Inspect the file:

```bash
hebrew-voice-to-text inspect call.wav
```

4. Create a job with two expected speakers:

```bash
CREATE_RESPONSE=$(hebrew-voice-to-text --env sandbox create-job call.wav --jobs-dir .hvt-jobs --expected-speakers 2)
JOB_ID=$(python -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<< "$CREATE_RESPONSE")
```

5. Run the job:

```bash
hebrew-voice-to-text --env sandbox run-job "$JOB_ID" --jobs-dir .hvt-jobs --output-dir out
```

6. Review speaker turns manually.
7. Copy only the approved action summary into the service system.

### Review questions

- Did the customer approve the change?
- Was a cancellation requested?
- Was a delivery date promised?
- Was a price or refund amount stated?
- Was a private value included in the external copy?

## Workflow 3: Freelancer voice memo to invoice notes

### Goal

Convert a Hebrew voice memo into work notes for billing.

### Example input

```text
היום עבדתי שלוש שעות על תיקון אתר, עוד שעה על פגישה, לחייב ₪1,200 עד 31/03/2026
```

### Steps

1. Transcribe local text or audio.
2. Detect amounts and dates.
3. Verify the amount against the contract.
4. Export Markdown for review.
5. Copy only confirmed line items to the invoice system.

### Output pattern

```text
דובר 1: היום עבדתי שלוש שעות על תיקון אתר, עוד שעה על פגישה, לחייב ₪1,200 עד 31/03/2026.
```

## Workflow 4: Supplier call to purchasing task

### Goal

Extract supplier commitments from a call without changing the meaning.

### Steps

1. Create a two-speaker job.
2. Label speakers as `ספק` and `עסק` during review.
3. Export JSON to keep timestamps.
4. Create follow-up tasks only from confirmed statements.
5. Keep uncertain words in the transcript until verified.

### Anti-pattern

Do not convert `אולי נשלח ביום ראשון` into `הספק ישלח ביום ראשון`. Keep uncertainty.

## Workflow 5: Training video captions

### Goal

Create subtitles for a Hebrew instructional video.

### Steps

1. Run provider transcription with timestamps.
2. Export SRT and VTT.
3. Limit subtitle segments to readable durations during manual review.
4. Check product names and technical terms.
5. Test captions in the target player.

### Quality targets

- Segment duration up to 7 seconds.
- Speaker labels only when useful.
- No private customer examples in public captions.
- Correct punctuation for questions and instructions.

## Workflow 6: Batch folder processing

### Goal

Create jobs for many files and process them consistently.

### Steps

1. Put input files in one folder.
2. Run the batch example:

```bash
python scripts/examples/example_batch_folder.py --env sandbox --folder ./audio --jobs-dir .hvt-jobs
```

3. Review the created job list.
4. Process jobs in small batches.
5. Track failures separately.

### Operational controls

- Use sandbox for new provider settings.
- Use production only after sample review passes.
- Keep source files read-only.
- Store outputs in a dated folder such as `out/15/03/2026`.

## Workflow 7: Privacy scan before sharing

### Goal

Prepare a transcript for sharing with a supplier, accountant, or customer.

### Steps

1. Render the transcript to TXT or Markdown.
2. Run the privacy scan example:

```bash
python scripts/examples/example_privacy_scan.py --env sandbox --text "הטלפון שלי 052-1234567"
```

3. Redact values that are not required by the recipient.
4. Keep full internal copy only when necessary.
5. Document why the copy was shared.

## Workflow 8: Provider comparison

### Goal

Compare providers without changing business rules.

### Steps

1. Use the same source file.
2. Use the same job request.
3. Run each provider command separately.
4. Compare word count, speaker consistency, punctuation, timestamps, and privacy warnings.
5. Select provider based on Hebrew quality, controls, and deletion path.

### Minimum sample set

- WhatsApp voice note.
- Two-speaker call.
- Noisy street clip.
- Finance-related customer message.
- Subtitle-oriented training clip.
