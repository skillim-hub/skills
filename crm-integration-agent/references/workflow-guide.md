# Workflow Guide

Use these workflows as production patterns. Run each workflow in sandbox mode before live writes.

## Workflow 1: WhatsApp quote request to Monday

Goal: turn a WhatsApp Business conversation into a Monday item for follow-up.

Steps:

1. Export or receive the WhatsApp message with stable message id.
2. Normalize phone to `+972` format.
3. Classify phrases such as `הצעת מחיר`, `כמה עולה`, or `אפשר מחיר` as sales.
4. Create a Monday item in the relevant board and group.
5. Store source channel, thread id, contact phone, last redacted message, and consent status.
6. Add a follow-up task for the owner.
7. Write audit events for every source message.

Acceptance checks:

- Customer phone is normalized.
- Monday item name remains in Hebrew.
- Last message contains no ID number, payment-card number, or verification code.
- Marketing opt-in remains false unless evidence exists.

## Workflow 2: Service email to HubSpot

Goal: create or update a HubSpot contact from an email thread about service or documents.

Steps:

1. Read message id, sender, subject, timestamp, and body summary.
2. Normalize email address.
3. Classify invoice, receipt, delivery, warranty, and complaint terms.
4. Search HubSpot by email and phone before create.
5. Update custom properties for source channel and thread id.
6. Add a service note rather than changing marketing subscription.
7. Save audit JSONL output.

Edge handling:

- If the email asks for חשבונית מס or קבלה, keep the CRM note as a service request. Store the official tax document in the accounting system.
- If the email includes attachments, store metadata and approved storage links only.

## Workflow 3: SMS appointment request to Salesforce

Goal: convert a customer SMS into a Salesforce lead or task for scheduling.

Steps:

1. Receive SMS webhook payload.
2. Normalize phone.
3. Classify terms such as `תור`, `פגישה`, or `לקבוע` as appointment.
4. Create or update a Salesforce lead.
5. Populate `Source_Channel__c`, `Source_Thread_ID__c`, and `Marketing_Opt_In__c`.
6. Create a scheduling task through the existing Salesforce process if available.
7. Write audit events.

Routing rule:

- Requests arriving outside Sunday through Thursday, 08:00 to 18:00, should create a next-business-day follow-up task.

## Workflow 4: Opt-out during service conversation

Goal: honor an opt-out while continuing service handling.

Steps:

1. Detect opt-out phrase such as `הסר`, `בטל`, `STOP`, or `unsubscribe`.
2. Mark marketing suppression in the CRM or marketing system.
3. Continue service conversation if the customer has an active issue.
4. Do not delete the service record solely because of the opt-out.
5. Record evidence and timestamp.

Decision rule:

- Opt-out controls marketing. It does not cancel obligations to provide service, warranty, delivery, billing, or appointment handling.

## Workflow 5: Legacy spreadsheet migration

Goal: move historical conversation rows into the normalized structure.

Steps:

1. Export spreadsheet as UTF-8 CSV.
2. Map columns to contact, thread, message, consent, and business purpose.
3. Normalize phone and email.
4. Deduplicate by external id, phone, then email.
5. Mark uncertain matches for manual review.
6. Run dry-run batches of 50 records.
7. Review generated payloads and warning counts.
8. Run production batches with audit output.

Stop conditions:

- More than 5 percent of rows lack phone, email, or external id.
- More than 2 percent of rows collide on multiple possible contacts.
- Any row contains unredacted payment-card numbers.

## Workflow 6: Complaint escalation

Goal: capture a consumer complaint and route it without over-collecting data.

Steps:

1. Classify words such as `תקול`, `לא הגיע`, `שבור`, or `אחריות` as support.
2. Redact sensitive identifiers from message body.
3. Store order number only if required for handling.
4. Add complaint note to CRM.
5. Route to support owner.
6. Keep marketing unchanged.
7. Log audit event.

## Workflow 7: Marketing consent capture

Goal: record consent evidence separately from service context.

Steps:

1. Accept only explicit phrases such as `אני מאשרת לקבל מבצעים`.
2. Store consent evidence, channel, and capture timestamp.
3. Keep a clear link between consent and the customer identifier.
4. Block marketing runs if evidence is absent.
5. Honor later opt-out immediately.

## Workflow 8: Attachment handling

Goal: avoid copying unnecessary files into CRM.

Steps:

1. Identify attachment type and business purpose.
2. Store filename, MIME type, source id, and approved storage link.
3. Do not store medical, legal, financial, or identity documents in CRM notes.
4. Redact body text before note creation.
5. Limit access to attachment storage by role.

## Rollback workflow

Use audit JSONL to locate affected source messages. Reverse only the CRM objects from the faulty run. Preserve the audit log. Disable the token used by the faulty run if scope or credential exposure is suspected.
