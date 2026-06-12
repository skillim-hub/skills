# Migration Checklist

Use this checklist when moving from manual or ad-hoc transcription to a controlled Hebrew voice-to-text workflow.

## Phase 1: Inventory

- List current sources: WhatsApp voice notes, call recordings, meeting audio, dictation files, video files.
- Record file types and average duration.
- Identify business owners for each source.
- Classify sensitivity for each source.
- Identify where transcripts are stored today.
- Identify who can access raw recordings.
- Identify retention rules for audio and transcripts.

## Phase 2: Consent and legal basis

- Document when consent is collected.
- Document alternative lawful basis where consent is not the basis.
- Define handling for customer calls.
- Define handling for employee, supplier, and minor voices.
- Define what must stop processing.
- Define escalation for high sensitivity content.

## Phase 3: Provider selection

- Verify `he-IL` recognition quality.
- Verify punctuation quality.
- Verify speaker labels or channel separation.
- Verify timestamp output.
- Verify UTF-8 JSON output.
- Verify deletion and retention settings.
- Verify access control and incident handling.
- Test with sandbox data before production.

## Phase 4: Package adoption

- Install with `pip install -e .`.
- Install development tools with `pip install -r requirements-dev.txt`.
- Configure `HVTT_ENV=sandbox`.
- Configure `HVTT_PROVIDER_COMMAND`.
- Run `pytest`.
- Run `python -m compileall scripts/ -q`.
- Create a sample job.
- Extract its id and show the provider-neutral request.
- Run a sample transcript.
- Review exported formats.

## Phase 5: Hebrew quality baseline

- Approve terminology for the business.
- Approve speaker label names.
- Approve date format `DD/MM/YYYY`.
- Approve currency format with `₪`.
- Approve uncertainty notation.
- Approve redaction style.
- Build a sample set with at least 10 representative files.

## Phase 6: Operational rollout

- Start with sandbox.
- Process a small controlled batch.
- Review every transcript manually.
- Track errors by source, provider, file type, and reviewer.
- Update troubleshooting notes.
- Promote to production only after acceptance criteria are met.
- Keep production access limited.

## Phase 7: Retention and deletion

- Define how long raw audio is retained.
- Define how long accepted transcripts are retained.
- Delete temporary converted files.
- Delete failed provider outputs that include sensitive data.
- Keep minimal audit data: date, job id, source file reference, output files, reviewer.
- Review retention quarterly.

## Phase 8: Ongoing controls

- Re-run test scenarios after provider changes.
- Re-run Hebrew QA after terminology changes.
- Re-run privacy checks after policy changes.
- Re-run package tests before release.
- Review provider contract changes.
- Keep sandbox and production configuration separate.

## Migration risks

| Risk | Mitigation |
|---|---|
| Old files contain private data | Inventory and minimize before migration. |
| Provider quality varies by audio type | Test representative samples. |
| Speaker labels are trusted too much | Require manual review for calls. |
| Staff share full transcripts unnecessarily | Provide redacted external copies. |
| Dates or amounts are copied incorrectly | Add manual review gate for business-critical fields. |
| Local scripts rely on path changes | Use editable install and package imports. |
