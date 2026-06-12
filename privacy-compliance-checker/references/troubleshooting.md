# Troubleshooting Guide

## Assessment problems

### Security level seems too high

Likely causes:

- A special-sensitivity category was supplied.
- The workflow is a public-body database, data-broker database, or direct-mailing-service database.
- A medium-level database contains information on 100,000 or more people.
- A medium-level database has more than 100 authorized users.
- Data broker or public body flag is true.

Fix:

1. Confirm whether the record count is 100,000 or more and whether authorized users exceed 100.
2. Remove categories that are not actually collected.
3. Split a mixed workflow into separate databases.
4. Keep conservative classification when facts are uncertain.

### Security level seems too low

Likely causes:

- Sensitive categories were omitted.
- Free text uses a local term that the tool does not recognize.
- Children, employee monitoring, or profiling flags were left false.
- Overseas contractor access was not treated as processor access.

Fix:

1. Add explicit categories such as `health`, `national_id`, `financial`, `children`, or `biometric`.
2. Mark `collects_children_data`, `employee_monitoring`, `uses_ai_profiling`, or `automated_decisions` when relevant.
3. Increase authorized user count only when suppliers or contractors can actually access the database or information.

### GDPR is not marked applicable

Likely causes:

- EU users were described only in a free-text purpose.
- `eu_targeting` or `eu_data_subjects` was not set.
- The business is a processor for an EU controller but the role was not documented.
- Behavior monitoring was not identified.

Fix:

1. Set `eu_targeting` to true when offering goods or services to EU or EEA people.
2. Set `eu_data_subjects` to true when processing EU or EEA personal data.
3. Add EU or EEA people to `data_subjects`.
4. Document the reason if GDPR is still not applied.

### Cross-border warning appears for a local business

Likely causes:

- Cloud hosting, email delivery, analytics, support, backups, or contractor access occurs outside Israel.
- Supplier terms permit access from multiple countries.
- Destination country was entered without checking adequacy or safeguards.

Fix:

1. Ask every supplier for storage, support, and subprocessor locations.
2. Record each country in `destinations`.
3. Complete a transfer assessment.
4. Reduce data sent to suppliers when safeguards are weak.

## CLI problems

### Command not found

Cause: Package was not installed in editable mode.

Fix:

```bash
pip install -e .
```

Then run:

```bash
privacy-compliance-checker --help
```

### Import fails in example scripts

Cause: The package is not installed and the command is executed from a different directory.

Fix:

```bash
pip install -e .
python scripts/examples/01_customer_club.py --env sandbox
```

### Create succeeds but get cannot find the ID

Cause: The create command and get command used different state directories.

Fix:

```bash
export PCC_STATE_DIR=.pcc-state
ID=$(privacy-compliance-checker create --scenario customer-club --format json | python -c 'import json,sys; print(json.load(sys.stdin)["id"])')
privacy-compliance-checker get "$ID" --format markdown
```

Or pass the same directory explicitly:

```bash
privacy-compliance-checker --state-dir .pcc-state create --scenario customer-club
privacy-compliance-checker --state-dir .pcc-state get pcc-example --format json
```

### JSON input fails

Cause: JSON was malformed or top-level value was not an object.

Fix:

```bash
python -m json.tool payload.json
privacy-compliance-checker validate payload.json
```

### Async tests fail

Cause: Development dependencies are missing.

Fix:

```bash
pip install -r requirements-dev.txt
pytest
```

## Documentation problems

### Hebrew notice uses mixed date formats

Use DD/MM/YYYY in Hebrew-facing documents. Example: 30/06/2026.

### Costs use non-local currency

Use ₪ for Israeli small-business examples unless a foreign supplier invoice is specifically discussed.

### Too much English in Hebrew text

Use established Hebrew terms:

| Avoid | Prefer |
|---|---|
| פרודקשן | סביבת ייצור |
| דאטה | מידע |
| ולידציה | בדיקה או אימות |
| קונטרולר | בעל שליטה |
| פרוססור | ספק עיבוד |
| קומפליינס | ציות |
| סקיוריטי | אבטחת מידע |
| דפלוימנט | הפעלה או הטמעה |

## Operational problems

### Supplier does not disclose subprocessor locations

Fix:

1. Ask for the data-processing addendum.
2. Ask for the subprocessor list.
3. Ask whether support access is global.
4. Escalate if sensitive data is involved.
5. Choose a supplier with clearer transfer terms when the risk is material.

### Retention period is unclear

Fix:

1. Split records by purpose.
2. Keep accounting records under accounting retention logic.
3. Keep suppression-list data only to prevent future marketing.
4. Delete stale lead notes.
5. Anonymize analytics after the business purpose expires.

### Data subject requests deletion but legal duties require retention

Fix:

1. Confirm identity.
2. Identify data categories.
3. Delete marketing, profile, and optional support data when possible.
4. Restrict records retained for legal or tax reasons.
5. Explain the retained categories and reason in plain language.
6. Schedule deletion when the legal hold expires.

### Incident team wants to clean systems before evidence is saved

Fix:

1. Preserve logs first.
2. Copy affected samples to a restricted evidence folder.
3. Record timeline and decisions.
4. Contain the issue.
5. Only then perform cleanup.
6. Keep a remediation tracker.

### Marketing team wants to reuse service data

Fix:

1. Identify the original purpose.
2. Check whether reuse is compatible.
3. Obtain consent when required.
4. Add unsubscribe and suppression controls.
5. Do not send until source and basis are recorded.

## Escalation triggers

Escalate beyond the tool when any of these occur:

- Health, biometric, genetic, credit, or criminal data.
- Large-scale minors data.
- Public body or statutory database.
- Data broker activity.
- Regulator inquiry.
- Litigation or threatened claim.
- Significant automated decision.
- Large breach or uncertain exposure.
- International transfer involving sensitive data and non-adequate destinations.
- Employee monitoring that captures private activity.
