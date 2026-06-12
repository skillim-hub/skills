# Migration Checklist

Use this checklist when moving from ad-hoc spreadsheets, older chat exports, manual tagging, or a previous package structure to `chat-data-analyzer`.

## Migration goals

- Standardize chat input.
- Replace legacy package-specific labels with neutral names.
- Preserve useful historical analysis while making outputs privacy-conscious.
- Convert manual labels into versioned custom intents.
- Make trend comparisons fair across old and new reports.

## Phase 1: Inventory

- [ ] List all chat sources: WhatsApp Business, web chat, CRM, inbox, marketplace, app, SMS, social messages.
- [ ] Identify export formats: CSV, JSON, JSONL, XLSX converted to CSV, copied chat text.
- [ ] Record available fields:
  - [ ] session/conversation ID
  - [ ] sender
  - [ ] text
  - [ ] timestamp
  - [ ] channel
  - [ ] assigned agent
  - [ ] status
  - [ ] tags
- [ ] Identify sensitive fields:
  - [ ] phone
  - [ ] email
  - [ ] Israeli ID-like value
  - [ ] card-like value
  - [ ] customer name
  - [ ] address
  - [ ] medical or child-related details
- [ ] Record current reporting metrics.
- [ ] Record current manual categories.

## Phase 2: Clean source exports

- [ ] Remove system rows that are not customer interaction.
- [ ] Remove marketing broadcasts unless the analysis is campaign-specific.
- [ ] Split group chats into customer sessions only when the business purpose is clear.
- [ ] Convert files to UTF-8.
- [ ] Normalize timestamps to ISO-8601 or `DD/MM/YYYY HH:MM:SS`.
- [ ] Map sender values:
  - [ ] customer → `user`
  - [ ] client → `user`
  - [ ] business → `bot`
  - [ ] agent → `bot`
  - [ ] assistant → `bot`
- [ ] Keep original raw export in restricted storage.
- [ ] Work on a copy.

## Phase 3: Standardize schema

Preferred JSON record:

```json
{
  "session_id": "source-date-number",
  "channel": "whatsapp",
  "messages": [
    {
      "sender": "user",
      "text": "אפשר לקבל חשבונית?",
      "timestamp": "2026-06-03T09:00:00"
    }
  ]
}
```

Preferred CSV columns:

```csv
session_id,sender,text,timestamp,channel
```

Checklist:

- [ ] Every row has `session_id`.
- [ ] Every customer/business message has `text`.
- [ ] Every sender is mapped.
- [ ] Timestamps are parseable.
- [ ] Date displays use `DD/MM/YYYY` in Israeli-facing outputs.
- [ ] Currency displays use ₪.

## Phase 4: Mask before sharing

Run:

```bash
python scripts/chat-data-analyzer-cli.py anonymize raw.json masked.json
```

Then verify:

- [ ] Emails are replaced with `[EMAIL]`.
- [ ] Israeli mobile numbers are replaced with `[PHONE]`.
- [ ] Valid Israeli ID-like values are replaced with `[ISRAELI_ID]`.
- [ ] Luhn-valid card-like values are replaced with `[CARD]`.
- [ ] Names and addresses are reviewed manually where needed.
- [ ] External vendors receive masked samples only.

## Phase 5: Establish baseline

Run:

```bash
python scripts/chat-data-analyzer-cli.py analyze masked.json --format json -o baseline-analysis.json
python scripts/chat-data-analyzer-cli.py analyze masked.json --format csv -o baseline-analysis.csv
```

Record:

- [ ] analysis date
- [ ] dataset period
- [ ] source system
- [ ] export filters
- [ ] analyzer version
- [ ] custom intent dictionary version
- [ ] conversation count
- [ ] top intent
- [ ] negative sentiment rate
- [ ] unresolved rate
- [ ] escalation rate
- [ ] drop-off rate

## Phase 6: Migrate manual labels to custom intents

Create a mapping table:

| Old manual label | New intent | Keywords | Owner | Review needed |
|---|---|---|---|---|
| חשבוניות | `billing_tax` | חשבונית, קבלה, מע״מ | finance | yes |
| תורים | `appointment` | תור, לקבוע, להזיז | service | no |
| משלוחים | `delivery` | משלוח, שליח, מספר מעקב | operations | no |
| החזרים | `cancellation_refund` | החזר, ביטול, זיכוי | service | yes |

Checklist:

- [ ] Merge duplicate old labels.
- [ ] Keep legal/tax conclusions out of classifier names.
- [ ] Avoid customer names and staff names as keywords.
- [ ] Avoid overly broad words as narrow intent keywords.
- [ ] Test custom intents on old and new samples.
- [ ] Store the dictionary with the report.

## Phase 7: Compare old and new reporting

Do not compare trend lines until filters match.

Confirm:

- [ ] Same date range.
- [ ] Same source systems.
- [ ] Same inclusion/exclusion rules.
- [ ] Same definition of resolved/unresolved.
- [ ] Same treatment of broadcasts.
- [ ] Same channel grouping.
- [ ] Same custom intent version.
- [ ] Same masking level for sample review.

If definitions changed, start a new baseline and annotate the dashboard.

## Phase 8: Replace old scripts

- [ ] Put `scripts/chat-data-analyzer-client.py` under version control.
- [ ] Put `scripts/chat-data-analyzer-cli.py` under version control.
- [ ] Move examples into `scripts/examples/`.
- [ ] Run tests:

  ```bash
  pytest -q scripts
  ```

- [ ] Add CI step if possible.
- [ ] Remove old scripts that contain outdated package-specific names or promotional text.
- [ ] Keep changelog entries for migration.

## Phase 9: Production readiness

- [ ] Define a weekly owner for chat analysis.
- [ ] Define a daily owner for unresolved chats.
- [ ] Define privacy owner for deletion/access/unsubscribe issues.
- [ ] Define finance owner for invoice, receipt, VAT, and refund issues.
- [ ] Define service manager for complaints and legal threats.
- [ ] Define retention for raw exports.
- [ ] Define retention for masked analytics.
- [ ] Define who can access raw examples.
- [ ] Define who can export dashboards.
- [ ] Review current Israeli legal, tax, privacy, consumer, and accessibility obligations.

## Phase 10: Rollback plan

Keep a rollback path for the first month.

- [ ] Store raw export separately from transformed files.
- [ ] Store the old report for comparison.
- [ ] Store custom dictionary versions.
- [ ] Store analysis outputs by date.
- [ ] Keep old dashboard read-only for one reporting cycle.
- [ ] Document metric definition changes.
- [ ] Revert to baseline labels if custom intents create unacceptable false positives.

## Migration risks and mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Old files contain personal data | Unauthorized exposure | Mask and restrict access. |
| Historical labels do not match new taxonomy | Trend breaks | Start a new baseline or map carefully. |
| WhatsApp exports include system noise | Inflated counts | Filter system lines. |
| Broadcasts mixed with support | Drop-off distortion | Split campaign data. |
| Timestamp formats vary | Missing response-time metrics | Normalize timestamps. |
| Custom terms too broad | Misclassification | Sample and refine. |
| Legal/tax wording embedded in code | Compliance risk | Keep approved text outside classifier. |
| Staff ignore dashboard | No improvement | Assign one owner and one action per review. |

## Migration sign-off template

```text
Migration date: DD/MM/YYYY
Dataset period:
Source systems:
Raw export location:
Masked export location:
Analyzer version:
Custom intent version:
Tests passed: yes/no
Reviewer:
Privacy review:
Finance review:
Service owner:
Known limitations:
Next review date:
```
