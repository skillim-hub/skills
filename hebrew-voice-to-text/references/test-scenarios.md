# Test Scenarios

Use these scenarios to evaluate Hebrew transcription quality, privacy handling, exports, and operational behavior. Each scenario includes input, expected behavior, and acceptance criteria.

## Scenario 1: Simple WhatsApp voice note

Input: one speaker says `שלום, אפשר לקבל חשבונית על ₪450`.

Expected behavior: transcript includes one speaker label, natural punctuation, and amount detection.

Acceptance criteria: `amount` appears in sensitive terms and output keeps `₪450`.

## Scenario 2: Customer asks a question

Input: `מה הסטטוס של ההזמנה`.

Expected behavior: terminal question mark.

Acceptance criteria: output ends with `?`.

## Scenario 3: Call with customer and business

Input: two speakers discussing delivery.

Expected behavior: two stable labels.

Acceptance criteria: no segment mixes both roles.

## Scenario 4: Phone number

Input: `תחזרו אליי ל-052-1234567`.

Expected behavior: phone detection and redaction.

Acceptance criteria: external copy shows `052-***4567`.

## Scenario 5: Identity-like number

Input: `תעודת זהות 123456789`.

Expected behavior: identity-like value detection.

Acceptance criteria: redacted copy shows `********9`.

## Scenario 6: Payment card

Input: `4111 1111 1111 1111`.

Expected behavior: payment card detection and replacement.

Acceptance criteria: redacted copy contains `[כרטיס טושטש]`.

## Scenario 7: Bank details hint

Input: `מספר חשבון בנק וסניף נשלחו בהודעה`.

Expected behavior: banking hint detection.

Acceptance criteria: sensitivity escalates to at least medium.

## Scenario 8: Date in Israeli format

Input: `הפגישה נקבעה ל-15/03/2026`.

Expected behavior: date remains in `DD/MM/YYYY`.

Acceptance criteria: no conversion to month-first order.

## Scenario 9: Date without year

Input: `ניפגש בחמישה עשר במרץ`.

Expected behavior: no guessed year.

Acceptance criteria: transcript marks the spoken date without adding a year unless context proves it.

## Scenario 10: Amount without currency

Input: `המחיר הוא ארבע מאות חמישים`.

Expected behavior: do not add `₪` automatically.

Acceptance criteria: reviewer note requests currency verification.

## Scenario 11: Noisy street recording

Input: short clip with background traffic.

Expected behavior: unclear words remain marked for review.

Acceptance criteria: no invented details.

## Scenario 12: Overlapping speech

Input: customer interrupts business response.

Expected behavior: short segments and lower confidence when provider supplies it.

Acceptance criteria: no merged commitment.

## Scenario 13: Supplier promise

Input: `אולי נשלח ביום ראשון`.

Expected behavior: uncertainty preserved.

Acceptance criteria: no conversion to a firm promise.

## Scenario 14: Cancellation request

Input: customer says `אני רוצה לבטל את ההזמנה`.

Expected behavior: action is preserved exactly.

Acceptance criteria: transcript clearly records cancellation.

## Scenario 15: Refund amount

Input: `תחזירו לי ₪120`.

Expected behavior: amount and request preserved.

Acceptance criteria: summary flags manual review.

## Scenario 16: Mixed Hebrew-English product name

Input: `צריך לתקן את ה-Shopify checkout`.

Expected behavior: product name remains as spoken.

Acceptance criteria: Hebrew prose around the product remains natural.

## Scenario 17: Customer name ambiguity

Input: name sounds like `דני` or `דנה`.

Expected behavior: mark uncertainty.

Acceptance criteria: final review does not guess.

## Scenario 18: Long training video

Input: 12-minute Hebrew tutorial.

Expected behavior: SRT and VTT exports.

Acceptance criteria: subtitles load in player and segment length is reviewed.

## Scenario 19: Single text file

Input: `sample.txt` with Hebrew text.

Expected behavior: local parsing without provider.

Acceptance criteria: TXT and JSON exports created.

## Scenario 20: Provider JSON with `text` only

Input: JSON with `text` and no `segments`.

Expected behavior: one default segment.

Acceptance criteria: parser creates `דובר 1`.

## Scenario 21: Invalid provider JSON

Input: provider writes logs to stdout before JSON.

Expected behavior: reject as invalid JSON.

Acceptance criteria: error instructs provider to print only JSON to stdout.

## Scenario 22: Missing provider response fields

Input: `{ "language": "he-IL" }`.

Expected behavior: reject response.

Acceptance criteria: error states that `segments` or `text` is required.

## Scenario 23: Sandbox job chain

Input: create job for text file and show it.

Expected behavior: create response includes `id`; show step accepts the same id.

Acceptance criteria: provider-neutral request contains matching id.

## Scenario 24: Production environment validation

Input: command with `--env production`.

Expected behavior: outputs carry production environment label.

Acceptance criteria: invalid environment values are rejected.

## Scenario 25: Batch folder

Input: folder with `.txt`, `.wav`, `.opus`, and unrelated files.

Expected behavior: jobs created only for supported files.

Acceptance criteria: unrelated files are skipped.

## Scenario 26: Compile check

Input: package source and scripts.

Expected behavior: all Python files compile.

Acceptance criteria: `python -m compileall scripts/ -q` exits with status 0.

## Scenario 27: Installable import

Input: fresh editable install.

Expected behavior: `from hebrew_voice_to_text import HebrewVoiceTextClient` works.

Acceptance criteria: no path manipulation is required.

## Scenario 28: Hebrew with niqqud

Input: Hebrew text containing vowel marks around the word `שלום`.

Expected behavior: marks removed.

Acceptance criteria: output is `שלום עולם.`.

## Scenario 29: Right-to-left control marks

Input: hidden direction marks around Hebrew text.

Expected behavior: control marks removed.

Acceptance criteria: output displays correctly in UTF-8 editor.

## Scenario 30: Manual review gate

Input: transcript with amount, date, and phone number.

Expected behavior: privacy and accuracy review before external sharing.

Acceptance criteria: review checklist is completed.
