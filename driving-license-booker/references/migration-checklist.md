# Migration Checklist

Use this checklist when replacing spreadsheets, ad hoc scripts, or manual notes.

## Inventory current process

- List every spreadsheet column or note field used today.
- Mark fields that contain personal data.
- Mark fields that contain official confirmation data.
- Separate official fee fields from private service fee fields.
- Identify duplicate customer records.

## Map fields

| Legacy field | New field | Action |
| --- | --- | --- |
| Customer name | `applicant.full_name` | Keep exact spelling from customer record. |
| ID number | `applicant.national_id` | Normalize and validate checksum. |
| Phone | `applicant.phone` | Normalize Israeli format. |
| License number | `applicant.license_number` | Keep as text. |
| Expiry | `expiry_date` | Convert to ISO in payload and DD/MM/YYYY in notes. |
| Paid | `has_paid_fee` | Store official ₪ receipt separately. |
| Branch | `windows.branch` | Use for bureau appointments. |
| City | `service_city` or `pickup_city` | Match workflow type. |
| Status | `status` | Map to draft, ready, submitted, confirmed, cancelled, or needs attention. |

## Cutover

1. Export legacy data to CSV.
2. Remove records that are no longer needed.
3. Normalize ID and phone values.
4. Import or recreate active requests only.
5. Run test scenarios with sandbox state file.
6. Train staff on the CLI quick-start and official-service boundaries.
7. Freeze legacy spreadsheet edits.
8. Keep a read-only archive for the retention period.
9. Start production state file for new requests.
10. Review exceptions after the first week.

## Rollback

- Keep the read-only legacy archive available until the new process is accepted.
- Export local JSON state before every major cleanup.
- Do not delete official receipts or confirmation numbers during rollback.
- Reconcile active appointments manually if the local state file is restored.


## Web-validation migration items for v3

- Replace any deprecated appointment host with GoVisit or the official Ministry appointment service page.
- Replace any vehicle-license payment link used for driver-license renewal with `/voucherspa/input/209`.
- Add practical-test fee handoff route `/voucherspa/input/427` only for practical driving-test fee payment.
- Remove any claim that the local package directly books official practical tests; record teacher or school confirmation instead.
- For VAT-registered businesses, verify the current VAT rate before issuing private-service invoices. The rate validated on 04/06/2026 is 18%.
