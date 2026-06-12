# Troubleshooting

## Literal Hebrew output

Cause: English syntax was copied into Hebrew.

Correction:

1. Move the action before optional details when natural.
2. Replace noun-heavy English with short Hebrew verbs.
3. Use Israeli business terms.
4. Read the sentence aloud.

Poor:

```text
בבקשה הנפק חשבונית מס/קבלה עבור 1,250 ₪ בתוספת מע״מ.
```

Better:

```text
נא להפיק חשבונית מס/קבלה על סך 1,250 ₪ בתוספת מע״מ.
```

## Overly casual output

Cause: slang or WhatsApp tone was used for a business or formal audience.

Correction:

- Replace `סבבה` with `אין בעיה`, `התקבל`, or `מאושר` according to context.
- Replace `יאללה` with a direct next step.
- Use `נא` for formal requests.
- Avoid exclamation marks in formal and legal-sensitive text.

## Wrong gender

Cause: English source did not reveal gender.

Correction:

- Prefer `נשמח לסייע`.
- Prefer `יש לשלוח`.
- Prefer `אפשר להמשיך`.
- Use slash forms only in short forms or constrained UI.

## Wrong VAT terminology

Cause: generic tax vocabulary was used.

Correction:

- Use `מע״מ` for VAT.
- Use `חשבונית מס` for a VAT invoice.
- Use `קבלה` for proof of payment.
- Use `חשבונית מס/קבלה` only when the source or accounting flow supports a combined document.
- Use `עוסק פטור` and `עוסק מורשה` for Israeli business status.

## Refund and cancellation wording sounds risky

Cause: translation created a stronger promise than the source.

Correction:

- Preserve conditions such as `subject to approval`, `unless required by law`, and `after inspection`.
- Avoid adding `מובטח` unless the source says guaranteed.
- Add a review note for consumer-protection text.

## Date confusion

Cause: US date order or ISO date remained in final Hebrew copy.

Correction:

- Convert `2026-03-05` to `05/03/2026`.
- Avoid `03/05/2026` unless the source already confirms day and month.
- Include the month name only when a channel requires extra clarity.

## URL or email changed

Cause: terminology replacement touched protected text.

Correction:

- Preserve URLs and email addresses exactly.
- Translate surrounding words only.
- Verify links after rendering in the final channel.

## Hebrew contains nikud

Cause: vowel marks were copied from a source or pasted from educational text.

Correction:

- Remove nikud from technical prose.
- Keep nikud only when quoting a name, brand, biblical phrase, or linguistic example that requires it.

## Right-to-left punctuation looks wrong

Cause: mixed Hebrew, English, numbers, and punctuation were rendered without review.

Correction:

1. Preview the exact final channel.
2. Move punctuation outside copied English tokens only when grammatically correct.
3. Keep URLs and emails on their own line when display is unstable.
4. Use bullets for mixed Hebrew-English lists.

## CLI cannot import the module

Cause: the package was not installed.

Correction:

```bash
pip install -e .
```

Then verify:

```bash
python -c "from hebrew_translation_assistant import HebrewTranslationAssistant; print(HebrewTranslationAssistant)"
```

## Stored request cannot be found

Cause: `HEBREW_TRANSLATION_ASSISTANT_HOME` changed between `create` and `show`, or the id was copied incorrectly.

Correction:

```bash
export HEBREW_TRANSLATION_ASSISTANT_HOME="$(pwd)/.hta-data"
hebrew-translation-assistant list
```

Use an id from the list output.

## Source-sensitive value is stale

Cause: a previous release or older source used a VAT, invoice-allocation, fee, form, or endpoint value without a current source check.

Fix:

- Check `references/verification-log.md` first.
- Use the release fact command: `hebrew-translation-assistant facts`.
- For Israel Invoices copy, flag the current release reference: 5,000 ₪ before VAT from 01/06/2026.
- For VAT copy, flag the current release reference: 18% from 01/01/2025.
- Require professional or official-source verification before publication, filing, or customer commitment.
