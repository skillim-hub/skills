# Migration Checklist

Use this checklist when moving from manual WhatsApp invoice handling, spreadsheet tracking, or an earlier automation.

## Inventory

- List all WhatsApp numbers and groups used for invoice intake.
- List current handlers: owner, office manager, bookkeeper, accountant, employees.
- List document types accepted: חשבונית מס, חשבונית מס/קבלה, קבלה, זיכוי, הצעה, דרישה.
- Identify current storage: phone gallery, Drive, email, bookkeeping system, spreadsheet, local computer.
- Measure monthly volume, peak days, duplicate rate, and review workload.
- Identify existing VAT, allocation-number, and retention checks.

## Target policy

- Choose allowed media: JPG, PNG, PDF.
- Decide whether screenshots and group chats are accepted.
- Configure approved senders and reply language.
- Define review blockers and reviewer permissions.
- Define export timing and correction workflow after export.
- Define retention for original images, OCR text, and chat metadata.

## Data model

Use records equivalent to: `whatsapp_events`, `media_files`, `invoice_extractions`, `invoice_reviews`, `invoice_exports`, `supplier_aliases`, `tenant_policies`, and `audit_events`.

Minimum imported record:

```json
{
  "message_id": "wamid.example",
  "sender_phone_hash": "sha256:...",
  "received_at": "2026-02-14T09:15:00+02:00",
  "source_file_sha256": "sha256:...",
  "document_type": "חשבונית מס/קבלה",
  "vendor_name": "א.ב. שירותים בע\"מ",
  "invoice_number": "8841",
  "issue_date": "2026-02-14",
  "total_amount": 117.0,
  "vat_amount": 18.0,
  "status": "accepted"
}
```

## Migration steps

1. Export existing images and PDFs to private storage.
2. Preserve original filenames and compute SHA-256 checksums.
3. Import existing spreadsheet rows as historical records.
4. Normalize dates to ISO and amounts to decimals.
5. Recalculate dedupe keys.
6. Mark already-booked records as exported or archived.
7. Run OCR/extraction in shadow mode.
8. Review differences against manual records.
9. Enable WhatsApp replies only after silent capture succeeds.
10. Enable bookkeeping export after duplicate and review controls are stable.

## Rollout phases

### Silent capture
Download, OCR, extract, and compare without automatic replies. Exit when clear invoices classify correctly and no privacy leaks appear in logs.

### Confirmation replies
Send accepted/unsupported replies, keep review semi-manual, monitor sender confusion and reply delivery.

### Bookkeeping export
Export only accepted records, block review and duplicates, reconcile weekly.

## Cutover checklist

Webhook HTTPS deployed; signature verification enabled; token storage secured; media storage private; Hebrew/English OCR configured; VAT policy set by effective date; allocation policy configured; review queue assigned; reply templates approved; export credentials tested; idempotency enabled; dashboards live; backup tested; old process frozen or redirected.

## Rollback

Disable automatic replies, stop export, keep safe webhook capture if possible, return to manual review from secure storage, preserve audit logs, fix the issue, reprocess in staging, then re-enable.
