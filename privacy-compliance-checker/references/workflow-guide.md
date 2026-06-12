# Workflow Guide

## Use pattern

Apply the same operating model to every workflow:

1. Define the business activity.
2. Map personal data fields, sources, recipients, systems, and retention.
3. Classify Israeli security level.
4. Check filing, notification, or authority-facing duties.
5. Check GDPR if EU targeting, monitoring, establishment, or processing is present.
6. Generate findings.
7. Assign owners, evidence, and due dates.
8. Re-test before production and after material change.

## Workflow 1: online store customer club

### Facts

- 18,000 customers.
- Names, phone numbers, email addresses, purchase history, birthday month.
- Email delivery provider outside Israel.
- Analytics and remarketing tags.
- Monthly coupons.

### Steps

1. Create the database specification.
2. Split purposes: order handling, loyalty benefits, receipts, marketing, analytics.
3. Record lawful basis per purpose.
4. Add unsubscribe and suppression-list logic.
5. Block optional tags until consent or another documented basis applies.
6. Review transfer to each destination country.
7. Execute processor terms with email and analytics providers.
8. Define retention: purchase records, marketing profile, consent proof, suppression list.
9. Test a deletion request that retains accounting records but removes marketing data.
10. Store evidence in a dated folder.

### Output evidence

- Versioned privacy notice.
- Consent log sample.
- Marketing suppression test.
- Transfer assessment.
- Processor terms.
- Retention schedule.
- Rights-request test.

## Workflow 2: freelancer client list

### Facts

- 350 leads and clients.
- Contact details, project notes, invoices.
- One cloud drive account.
- No sensitive data.
- No EU targeting.

### Steps

1. Define purposes: client management, proposals, invoicing, support.
2. Remove stale leads or set a review period.
3. Restrict drive sharing.
4. Turn on multi-factor authentication.
5. Publish a short privacy notice.
6. Separate accounting records from marketing or lead notes.
7. Create a deletion process for old prospects.
8. Document the cloud provider as a processor or service provider with transfer facts.

### Output evidence

- Short inventory.
- Access settings screenshot or export.
- Retention decision.
- Privacy notice.
- Backup check.

## Workflow 3: private clinic

### Facts

- 12,000 patient records.
- Health information, ID numbers, appointment history, payment references.
- Appointment platform and billing provider.
- Staff access from clinic workstations.

### Steps

1. Classify the statutory security level as medium unless the database reaches 100,000 or more people, more than 100 authorized users, or another high-level trigger. Treat operational severity as high due to health data.
2. Prepare a detailed database specification.
3. Restrict access by role.
4. Enable logging and review exceptional access.
5. Sign processor terms.
6. Test backup restoration.
7. Train staff on information with special sensitivity and wrong-recipient incidents.
8. Publish clear patient notice.
9. Run a rights-request tabletop exercise.
10. Maintain incident escalation contacts.

### Output evidence

- Access matrix.
- Log review record.
- Restore test.
- Staff training record.
- Processor register.
- Incident procedure.
- Notice version.

## Workflow 4: breach triage

### Facts

- A customer export was sent to the wrong recipient.
- File contained names, phone numbers, purchase amounts, and loyalty status.
- Recipient says the file was deleted.

### Steps

1. Open an incident log.
2. Preserve mail logs, file-sharing logs, and the exported sample.
3. Request written deletion confirmation.
4. Disable public or external links.
5. Identify affected people and fields.
6. Determine whether sensitive information or large-scale exposure is involved.
7. Decide whether Israeli authority notification is required.
8. If GDPR applies, assess 72-hour supervisory authority reporting.
9. Prepare affected-person notice if required.
10. Add remediation: export approval, masking, recipient warning, and access review.

### Output evidence

- Incident timeline.
- Affected-record count.
- Risk assessment.
- Notification decision.
- Deletion confirmation.
- Remediation tickets.

## Workflow 5: cloud service with EU users

### Facts

- Israeli cloud service.
- EU customers use the service.
- Hosting in Germany.
- Support and logs accessible from the United States.
- Product analytics and optional profiling.

### Steps

1. Mark GDPR as applicable.
2. Prepare GDPR processing record.
3. Map controller and processor roles for each customer.
4. Sign processor terms.
5. Review standard contractual clauses or other transfer mechanism for non-adequate destinations.
6. Screen for data-protection impact assessment.
7. Document analytics and profiling logic.
8. Provide rights intake and customer support playbook.
9. Test deletion, export, and access request workflows.
10. Add breach reporting clock and customer notification commitments.

### Output evidence

- Processing record.
- Data-processing terms.
- Transfer assessment.
- Subprocessor list.
- DPIA screening.
- Rights test.
- Breach playbook.

## Workflow 6: consumer complaint against a business

### Facts

- Consumer receives marketing messages after unsubscribe.
- Business claims the consumer is still an active customer.
- Consumer wants deletion and proof of source.

### Steps

1. Separate service notices from marketing.
2. Ask for source, basis, and unsubscribe status.
3. Check whether the suppression list was bypassed.
4. Remove marketing eligibility.
5. Keep minimum suppression data if needed to prevent future marketing.
6. Delete or anonymize unrelated profile fields.
7. Provide a short response explaining actions taken.
8. Retain evidence of the request and completion.

### Output evidence

- Request log.
- Consent or source record.
- Suppression entry.
- Response copy.
- Deletion or anonymization record.

## Workflow 7: employee monitoring

### Facts

- Employer wants to track work laptops and productivity.
- Employees work from home.
- Tool can capture app usage and screenshots.

### Steps

1. Define the legitimate workplace purpose.
2. Test less intrusive alternatives.
3. Disable screenshot capture unless essential and reviewed.
4. Give clear advance notice.
5. Limit access to managers with a need to know.
6. Set retention period.
7. Exclude private areas and breaks where possible.
8. Review outputs for accuracy and proportionality.

### Output evidence

- Necessity memo.
- Employee notice.
- Access list.
- Retention rule.
- Review record.

## Workflow 8: migration from spreadsheet to managed system

### Facts

- Business has several spreadsheets with leads, customers, and invoices.
- Files are copied to personal devices.
- New managed system is planned.

### Steps

1. Inventory all spreadsheets and owners.
2. Remove duplicates and stale leads.
3. Classify sensitive fields.
4. Import only necessary data.
5. Restrict exports in the new system.
6. Migrate consent proof and suppression lists.
7. Delete obsolete copies after validation.
8. Document post-migration access and retention.

### Output evidence

- Migration inventory.
- Cleansing log.
- Import mapping.
- Access settings.
- Deletion confirmation.
- Post-migration report.

## Workflow 9: supplier onboarding

### Facts

- New support provider will access customer tickets.
- Some tickets may include sensitive attachments.
- Provider uses subcontractors.

### Steps

1. List accessed fields.
2. Confirm countries of storage and support access.
3. Sign processor terms.
4. Require subprocessor disclosure.
5. Limit support access to tickets assigned to the provider.
6. Add breach notification duties.
7. Add deletion or return at termination.
8. Review evidence annually.

### Output evidence

- Supplier questionnaire.
- Processing terms.
- Access configuration.
- Subprocessor list.
- Annual review record.

## Workflow 10: privacy notice update

### Facts

- Business adds analytics, new payment provider, and overseas support.

### Steps

1. Update recipients and processors.
2. Add transfer destinations.
3. Explain analytics categories.
4. Update rights channel.
5. Version the notice with date in DD/MM/YYYY format for Hebrew audiences.
6. Publish before the change starts.
7. Keep a copy of the previous notice.
8. Notify users when the change is material.

### Output evidence

- New notice.
- Previous notice.
- Change log.
- Publication record.
- User notice if material.
