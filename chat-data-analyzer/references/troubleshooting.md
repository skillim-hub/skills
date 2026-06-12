# Troubleshooting Guide

Use this guide when validation fails, Hebrew labels look wrong, metrics are surprising, or production review finds gaps.

## 1. Input and encoding problems

### Symptom: JSON fails to load

**Common causes**

- Trailing commas.
- Unescaped line breaks inside text.
- File saved as Windows-1255 or another non-UTF-8 encoding.
- A JSONL export was saved with `.json`.

**Fix**

1. Save the file as UTF-8.
2. Use `.jsonl` for one JSON object per line.
3. Validate with:

   ```bash
   python -m json.tool chats.json >/tmp/validated.json
   ```

4. For JSONL, validate line by line:

   ```bash
   python - <<'PY'
   import json
   from pathlib import Path
   for i, line in enumerate(Path("chats.jsonl").read_text(encoding="utf-8").splitlines(), 1):
       if line.strip():
           json.loads(line)
   print("ok")
   PY
   ```

### Symptom: Hebrew appears as `\u05e9\u05dc...`

**Cause:** JSON was serialized with ASCII escaping.

**Fix:** use `ensure_ascii=False` when writing JSON. The included client already does this in `to_json`.

### Symptom: CSV has broken Hebrew

**Common causes**

- Spreadsheet saved as ANSI.
- UTF-8 BOM mismatch.
- Commas inside messages without proper quoting.

**Fix**

- Export as UTF-8 CSV.
- Quote text fields.
- Prefer JSON if messages contain line breaks, commas, emojis, or URLs.

### Symptom: CSV validation says required columns are missing

**Required columns**

- `session_id`
- `sender`
- `text`

**Fix**

Rename columns before analysis. Acceptable optional timestamp columns: `timestamp`, `created_at`.

## 2. Timestamp problems

### Symptom: `Unsupported timestamp format`

**Supported formats**

- `2026-06-03T14:05:00`
- `2026-06-03T14:05:00+03:00`
- `03/06/2026 14:05:00`
- `03/06/2026 14:05`
- `03/06/2026 14:05:00`

**Fix**

Normalize timestamps during export:

```python
from datetime import datetime

dt = datetime.strptime("03/06/2026 14:05", "%d/%m/%Y %H:%M")
print(dt.isoformat())
```

### Symptom: response time is empty

**Common causes**

- Missing timestamps.
- Messages are not sorted.
- Only one side of the conversation has timestamps.
- Bot message timestamp is earlier than user message timestamp.

**Fix**

1. Sort by timestamp inside each `session_id`.
2. Ensure both user and bot messages include timestamps.
3. Drop imported system rows that appear between user and bot messages.

## 3. Sender mapping problems

### Symptom: `Unsupported sender`

**Accepted customer senders**

- `user`
- `customer`
- `client`

**Accepted business/bot senders**

- `bot`
- `assistant`
- `agent`
- `business`

**Fix**

Map source-specific senders before analysis:

```python
sender_map = {
    "לקוח": "user",
    "עסק": "bot",
    "נציג": "bot",
}
```

### Symptom: escalation rate is too high

**Common cause:** agent messages are labeled as `user`.

**Fix:** verify sender mapping. A business message such as “נציג יחזור אליך” should usually be `bot` or `business`, not `user`.

## 4. Intent classification problems

### Symptom: too many `unknown` intents

**Common causes**

- Business-specific terms are missing.
- Product names dominate the chat.
- Messages are too short.
- Source export removed customer text.

**Fix**

1. Review `top_terms`.
2. Add custom intents:

   ```python
   custom = {
       "subscription": ["מנוי", "חידוש מנוי", "מסלול חודשי"],
       "course_registration": ["הרשמה לקורס", "שיעור ניסיון", "סדנה"]
   }
   analyzer = ChatDataAnalyzerClient(custom_intents=custom)
   ```

3. Rerun analysis.
4. Manually review 20 samples.

### Symptom: billing/tax catches too many chats

**Common causes**

- “מחיר” appears in many sales questions.
- “זיכוי” appears in refund and invoice contexts.
- Product support uses “חיוב” loosely.

**Fix**

- Use top two intent scores, not only the first label.
- Add a custom narrower sales intent if price questions dominate.
- Review chats with both `billing_tax` and `sales_lead` scores.

### Symptom: delivery and refund are mixed

**Common cause:** customers often write “המשלוח לא הגיע, רוצה החזר”.

**Fix**

Treat this as a combined operational issue:
- primary owner: logistics if delivery terms dominate
- secondary owner: service/finance if refund terms dominate
- escalation: service manager if sentiment is negative

### Symptom: legal/privacy intent appears for normal newsletter questions

**Fix**

Do not rely on a single keyword. Review hits:
- `הסר`, `ספאם`, `לא נתתי הסכמה`, `תמחקו`, `פרטיות` require priority.
- General “רשימת תפוצה” may only need marketing routing.

## 5. Sentiment problems

### Symptom: sentiment is too negative

**Common causes**

- “דחוף” appears in normal Israeli service language.
- Shipping delays contain operational words even when the customer is calm.
- A resolved conversation includes one negative message at the start.

**Fix**

- Use sentiment together with `resolution_status`.
- Review final messages. “תודה, הסתדר” may indicate recovery.
- Add business-specific positive recovery phrases.

### Symptom: sentiment misses sarcasm

Example:

```text
איזה יופי, שוב האתר נפל.
```

**Fix**

- Add repeated sarcastic phrases only after manual sampling.
- Mark sarcasm-heavy clusters for human review.

### Symptom: positive sentiment appears in complaints

**Common causes**

- “תודה” appears after a complaint.
- A customer begins politely before stating a problem.
- Negation scope is complex.

**Fix**

- Sort by both `sentiment.label` and intent.
- Use `complaint`, `delivery`, and `technical_support` as risk indicators even if sentiment is neutral.

## 6. Sensitive-data detection problems

### Symptom: too many Israeli ID-like flags

**Cause:** some order numbers are 9 digits and may pass checksum rarely.

**Fix**

- Keep flags as possible identifiers, not confirmed identifiers.
- Mask before sharing if there is doubt.
- Use order-number prefixes to reduce false positives in a custom preprocessing step.

### Symptom: card-like values are not detected

**Cause:** only Luhn-valid card-like numbers are flagged to reduce false positives.

**Fix**

- For strict environments, add a custom rule that masks any 13–19 digit sequence.
- Avoid storing full payment details in chat exports.

### Symptom: names are not masked

**Cause:** deterministic name detection in Hebrew is unreliable without a business-specific list or model.

**Fix**

- Do not rely on this package for full anonymization.
- Add known customer/staff name lists only when appropriate.
- Prefer manual review for external sharing.

## 7. Metric interpretation problems

### Symptom: drop-off rate is high

**Common causes**

- Marketing broadcasts imported as conversations.
- Last customer message is a normal closing phrase.
- Bot asks too many follow-up questions.
- Human handoff happened outside the exported system.

**Fix**

1. Remove broadcasts.
2. Sample last-turn conversations.
3. Add closure phrases to the resolved set if they are common.
4. Join external agent handoff data where available.

### Symptom: unresolved rate is high

**Common causes**

- Final customer questions are unanswered.
- Human-agent requests are not closed in the dataset.
- Negative chats are counted even after offline resolution.

**Fix**

- Add external status fields if CRM data exists.
- Use `resolution_status`, not only `unresolved`.
- Add a manual “closed” override in downstream dashboards if needed.

### Symptom: top intent changes after adding custom terms

**Cause:** custom intent scores compete with defaults.

**Fix**

- Compare before/after distributions.
- Keep a migration note.
- Manually sample changed labels before using trend comparisons.

## 8. CLI problems

### Symptom: `ModuleNotFoundError: click`

**Fix**

Install runtime and development requirements:

```bash
python -m pip install -e .
python -m pip install -r requirements-dev.txt
```

Or install Click directly:

```bash
python -m pip install click
```

### Symptom: CLI works locally but not in CI

**Common causes**

- Python version below 3.10.
- Running from a directory that cannot access `scripts/chat-data-analyzer-client.py`.
- File path quoting issues with Hebrew filenames.

**Fix**

- Use Python 3.10+.
- Run commands from the package root.
- Quote paths:

  ```bash
  python scripts/chat-data-analyzer-cli.py analyze "exports/שיחות יוני.json"
  ```

## 9. Test suite problems

### Symptom: pytest cannot import the client

**Cause:** the script file uses hyphens and must be loaded by path.

**Fix**

Use the provided tests as the pattern:

```python
import importlib.util
from pathlib import Path

path = Path("scripts/chat-data-analyzer-client.py")
spec = importlib.util.spec_from_file_location("chat_data_analyzer_client", path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
```

### Symptom: async tests hang

**Fix**

- Use `asyncio.run` for simple tests.
- Avoid nested event loops in notebooks.
- Keep heavy IO out of the async wrapper; it delegates to thread execution.

## 10. Production reliability problems

### Symptom: weekly charts are inconsistent

**Common causes**

- Date range changed.
- Source export changed.
- New custom intents changed labels.
- Broadcasts or internal chats were included.

**Fix**

- Store export parameters with each run.
- Keep code and custom dictionaries versioned.
- Use the migration checklist before comparing old and new reports.

### Symptom: staff do not act on insights

**Fix**

Keep the weekly review operational:
- one top issue
- one owner
- one action
- one follow-up date
- no more than five metrics

## 11. Safe fallback rules

When uncertain:

1. Mask more data, not less.
2. Escalate legal/privacy/accounting chats.
3. Treat sentiment as triage, not truth.
4. Sample manually before changing customer-facing copy.
5. Verify current Israeli legal or tax obligations before turning analysis into policy.
