# Troubleshooting

## Fast diagnosis

| Question | Command or check |
|---|---|
| Does the package import? | `python -c "import crm_integration_agent; print(crm_integration_agent.__version__)"` |
| Does the CLI load? | `crm-integration-agent --help` |
| Is the phone valid? | `crm-integration-agent normalize-phone "050-123-4567"` |
| Is the payload valid before network writes? | `crm-integration-agent dry-run --provider hubspot --input thread.json --env sandbox` |
| Are tests passing? | `python -m pytest -q` |
| Is syntax valid? | `python -m compileall scripts/ -q` |

## Common failures

### Missing identifier

Error:

```text
Contact requires phone, email, or external_id
```

Fix:

- Add normalized phone, email, or a source-system customer id.
- Do not create CRM records from name alone.

### Invalid Israeli phone

Error:

```text
Invalid Israeli phone
```

Fix:

- Accept forms such as `050-123-4567`, `03-555-1234`, `+972501234567`, or `00972501234567`.
- Reject short numbers and internal extensions as CRM identifiers.

### Marketing consent blocked

Error:

```text
Marketing action requires explicit opt-in
```

Fix:

- Add evidence such as `אני מאשרת לקבל מבצעים`.
- Run service-only workflows when consent is unavailable.
- Treat `הסר`, `בטל`, and `STOP` as suppression signals.

### Hebrew output appears escaped

Symptom:

```json
"\u05d3\u05e0\u05d4"
```

Fix:

```python
json.dumps(payload, ensure_ascii=False, indent=2)
```

### Salesforce base URL missing

Error:

```text
Salesforce requires base_url
```

Fix:

```bash
export SALESFORCE_BASE_URL="https://example.my.salesforce.com"
```

### Provider returns 401 or 403

Fix:

- Confirm the correct environment token is loaded.
- Verify scopes for the object being created.
- Rotate a token if it may have been exposed.

### Provider returns 409

Fix:

- Query existing records by external id, phone, then email.
- Change the run from create to update.
- Keep the original audit event and add a conflict-resolution event.

### Duplicate contacts after migration

Fix:

1. Export CRM records with phone, email, external id, and created time.
2. Normalize identifiers locally.
3. Group by external id, then phone, then email.
4. Send name-only matches to manual review.
5. Merge through the CRM native merge tool.

### Attachments not visible in CRM

Fix:

- Store attachment metadata in CRM.
- Store files in approved storage with role-based access.
- Avoid copying sensitive files directly into CRM notes.

## Retry policy

| Condition | Retry |
|---|---|
| Local validation error | No. Fix data. |
| 401 or 403 | No. Fix token or scope. |
| 409 duplicate conflict | No automatic retry. Resolve match. |
| 429 rate limit | Yes, with exponential backoff. |
| 500 to 599 | Yes, with idempotency key. |
| Network timeout | Yes, then verify whether provider created the object. |

## Escalation package

When escalating an issue internally, include:

- Sanitized source thread JSON.
- Dry-run output.
- Provider response status and sanitized body.
- Audit JSONL lines for the affected messages.
- Destination object id if one was created.
- Timestamp and environment.

Never include full payment-card numbers, verification codes, or unnecessary identity documents in escalation material.


### Validated endpoint mismatch

Symptoms:

```text
HTTP 404 endpoint not found after provider upgrade
```

Fixes:

- Use HubSpot `/crm/objects/2026-03/contacts` for new integrations.
- Use Salesforce `/services/data/v67.0/sobjects/Lead` unless a sandbox test proves a different pinned version is required.
- Keep Monday GraphQL calls on `https://api.monday.com/v2`.
