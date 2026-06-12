# Migration Checklist

Use this checklist when moving from ad hoc privacy handling to a controlled workflow. It applies to spreadsheets, unmanaged customer lists, shared inboxes, small cloud systems, and new vendor platforms.

## Phase 1: inventory

- List every file, system, database, form, inbox, device, and supplier that contains personal data.
- Record owner, location, access list, purpose, categories, and approximate record count.
- Flag sensitive information, children data, employee data, ID numbers, financial data, health information, precise location, and free-text notes.
- Identify duplicate lists and unofficial exports.
- Mark systems with overseas access, hosting, support, backup, or analytics.

## Phase 2: classification

- Classify each workflow as basic, medium, or high security level.
- Record why each level was chosen.
- Mark workflows that may require current filing or notification review.
- Mark workflows with GDPR applicability.
- Mark workflows with direct marketing, tracking, profiling, or automated decisions.
- Mark workflows with processor and transfer dependencies.

## Phase 3: data cleansing

- Remove obsolete leads.
- Delete duplicate exports.
- Separate accounting records from marketing and support data.
- Remove sensitive fields that are not necessary.
- Replace full identifiers with partial identifiers where possible.
- Redact sensitive attachments in support tickets where full content is not needed.
- Keep deletion evidence.

## Phase 4: lawful basis and notice

- Assign a lawful basis to every purpose.
- Draft or update the privacy notice.
- Use Hebrew for Israeli consumer workflows.
- Use DD/MM/YYYY dates in Hebrew-facing notices.
- Include ₪ amounts when examples discuss local fees, charges, refunds, or subscription costs.
- Explain recipients, transfers, retention, and rights.
- Publish the notice before the new workflow starts.
- Preserve the previous notice when changing a live workflow.

## Phase 5: supplier and transfer controls

- List every processor.
- Ask for data-processing terms.
- Ask for subprocessor and location details.
- Record transfer destinations.
- Complete transfer assessment for each non-local destination.
- Restrict supplier access to necessary data.
- Require incident notice.
- Define return or deletion at termination.
- Store supplier evidence.

## Phase 6: access and security

- Replace shared accounts with named accounts.
- Apply least privilege.
- Enable multi-factor authentication for administrative access.
- Configure access logs where required.
- Review permissions before launch.
- Configure backups.
- Test restoration.
- Restrict exports.
- Document device and remote-access rules.

## Phase 7: marketing controls

- Store source or consent for each marketing recipient.
- Separate service messages from marketing.
- Add unsubscribe to each marketing message.
- Maintain suppression lists.
- Block optional advertising tags until permitted.
- Test opt-out end to end.
- Delete stale marketing profiles while keeping minimal suppression records where needed.

## Phase 8: rights handling

- Create an intake channel.
- Define identity verification.
- Create response templates.
- List systems that must be searched.
- Track deadlines and decisions.
- Define partial deletion and legal-hold logic.
- Train staff who receive customer requests.
- Test a sample access request and deletion request.

## Phase 9: incident readiness

- Create an incident log template.
- Define containment steps.
- Define evidence preservation.
- Define severity assessment.
- Define notification decision workflow.
- Include Israeli notification review.
- Include GDPR 72-hour review where applicable.
- Store emergency supplier contacts.
- Run a tabletop exercise.

## Phase 10: cutover

- Freeze old exports.
- Import only approved data.
- Validate record counts.
- Validate permissions.
- Validate notices and consent controls.
- Validate unsubscribe and deletion.
- Validate backups.
- Delete or archive legacy files according to the retention schedule.
- Record the cutover date.
- Assign the next review date.

## Phase 11: post-migration review

Perform the review within 30 days of launch:

- Compare imported fields against approved fields.
- Check unexpected sensitive data.
- Confirm users still need access.
- Confirm logs are collected.
- Confirm suppliers match the approved list.
- Confirm transfers match the approved list.
- Check open rights requests.
- Check incidents or near misses.
- Update risk assessment.
- Document management approval.

## Evidence folder structure

```text
privacy-evidence/
  01-inventory/
  02-notices/
  03-lawful-basis/
  04-security/
  05-suppliers/
  06-transfers/
  07-marketing/
  08-rights/
  09-incidents/
  10-reviews/
```

## Go-live gate

Do not launch when any item below is unresolved:

- No lawful basis for a purpose.
- Sensitive data lacks notice and access controls.
- Processor has production access without processing terms.
- Overseas access exists without transfer assessment.
- Marketing lacks opt-out.
- Optional tracking loads before consent where consent is required.
- No way to handle access, correction, deletion, or objection requests.
- No incident escalation path.
- No retention decision.
- Shared administrator account remains active.
