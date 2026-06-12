# Migration Checklist

Use this checklist when moving from spreadsheets, calendar reminders, messaging notes, or another property management tool.

## Before migration

1. Freeze edits in the source system for the migration window.
2. Export properties, tenants, leases, rent payments, maintenance tasks, and communications separately.
3. Back up the original files.
4. Remove duplicate rows and obsolete tenants.
5. Decide which historical records must remain read-only.
6. Confirm privacy basis for keeping personal data.
7. Mask identity numbers unless full values are legally required.
8. Define sandbox and production store paths.

## Field mapping

| Source field | Target field | Rule |
|---|---|---|
| Property address | `PropertyRecord.address` | Keep Hebrew spelling as used in official documents. |
| City | `PropertyRecord.city` | Normalize common spelling variants manually. |
| Apartment | `PropertyRecord.apartment` | Include floor only if operationally needed. |
| Tenant name | `TenantRecord.full_name` | Use full legal name where available. |
| Phone | `TenantRecord.phone` | Convert to Israeli local or +972 format. |
| Email | `TenantRecord.email` | Validate before import. |
| Lease start | `LeaseRecord.start_date` | Convert to ISO internally after DD/MM/YYYY import. |
| Lease end | `LeaseRecord.end_date` | Reject end before start. |
| Monthly rent | `LeaseRecord.monthly_rent_ils` | Store numeric ₪ amount with two decimals. |
| Deposit | `LeaseRecord.deposit_ils` | Do not import as rent charge. |
| Due day | `LeaseRecord.due_day` | Use 1 to 28. |
| Payment date | `RentCharge.paid_date` | Keep bank reference where available. |
| Maintenance note | `MaintenanceTask.description` | Preserve exact tenant report when possible. |

## Import order

1. Import properties.
2. Import tenants and link each tenant to a property.
3. Import leases and link each lease to property and tenant.
4. Generate or import rent charges.
5. Record payments against charges.
6. Import open maintenance tasks.
7. Import communication logs only if needed for continuity.
8. Run duplicate checks.
9. Export accounting pack for a sample period and compare with the source.

## Validation checks

1. Every lease links to an existing property and tenant.
2. No rent charge exists after lease end date.
3. No duplicate charge exists for the same lease and due date.
4. Paid rent totals match bank reconciliation.
5. Deposit records are separate from rent records.
6. Open urgent maintenance tasks are reviewed first.
7. Tenant communication preferences are valid.
8. Hebrew text remains readable in JSON.

## Rollback plan

1. Keep the original source export unchanged.
2. Keep a copy of the pre-import JSON store.
3. Run migration into sandbox first.
4. Compare counts and totals.
5. Delete the sandbox store if validation fails.
6. Apply corrections to source mapping, not directly to production records.
7. Re-run migration.
8. Switch to production only after sign-off.

## Post-migration checklist

1. Run `pytest -q`.
2. Run `python -m compileall scripts/ -q`.
3. Generate the next month of rent charges.
4. Build the next daily agenda.
5. Review all open maintenance tasks.
6. Send no automated messages until templates are reviewed.
7. Store backup in an access-controlled location.
8. Record the migration date and reviewer.


## Validated reference values

1. After migration, run `property-management-scheduler reference-values --as-of 01/06/2026`.
2. Confirm that commercial invoice review thresholds, VAT reference, and Bank of Israel host match current official sources.
3. Record the verification date in the migration handoff notes.
