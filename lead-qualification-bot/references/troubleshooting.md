# Troubleshooting

## Diagnostic sequence

1. Confirm the inbound webhook received the message.
2. Confirm Hebrew text is decoded as UTF-8.
3. Confirm the phone is normalized to E.164.
4. Confirm session state loaded.
5. Confirm extraction of service, city, urgency, budget, consent, and opt-out.
6. Confirm score, tier, owner, and SLA.
7. Confirm outbound WhatsApp status.
8. Confirm CRM or CSV export.
9. Confirm handoff and suppression rules.

## Common issues

| Symptom | Likely cause | Fix |
|---|---|---|
| Repeated question | State not saved | Persist after each inbound event |
| Hebrew gibberish | Encoding problem | Use UTF-8 or UTF-8 with BOM |
| Good leads score low | Missing aliases or budget too strict | Add city/service synonyms and neutral budget points |
| Poor leads score hot | No disqualifiers | Require service match and add spam/out-of-area rules |
| Opt-out ignored | Keyword list too narrow | Detect הסרה, להסיר, STOP, unsubscribe, לא לשלוח |
| CRM duplicates | No idempotency | Use WhatsApp message ID and normalized phone |
| Attachments fail | Expired media or permission | Download promptly or request resend if essential |
| Template rejected | Wrong category or unclear text | Separate utility and marketing templates |
| Users abandon | Too many questions | Ask three critical questions before handoff |
| Hot leads unassigned | Missing owner | Configure default hot queue and alert |

## Incident playbooks

### Privacy incident

1. Stop affected exports.
2. Identify records and fields.
3. Preserve audit logs.
4. Remove exposed access.
5. Rotate credentials.
6. Review notification obligations with qualified counsel.
7. Document root cause and remediation.

### WhatsApp outage

1. Stop retry storm.
2. Queue inbound events.
3. Publish alternate contact path if needed.
4. Replay with idempotency checks.
5. Review missed hot leads.

### CRM outage

1. Queue leads locally in protected storage.
2. Continue WhatsApp acknowledgment.
3. Alert owner manually for hot leads.
4. Replay when the CRM returns.

## Logs to capture

request_id, wa_message_id, phone_e164, language, extracted_fields, score, tier, handoff_reason, consent_status, outbound_status, crm_status, retry_count.

## Useful commands

```bash
pytest -q
python scripts/lead-qualification-bot-cli.py qualify --message "צריך תיקון דחוף היום בתל אביב תקציב 500 שח" --phone "0501234567"
python scripts/lead-qualification-bot-cli.py batch --input scripts/examples/sample_leads.csv --output /tmp/qualified.csv
```
