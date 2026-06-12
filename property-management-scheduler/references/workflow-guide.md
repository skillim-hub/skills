# Workflow Guide

## Workflow 1: Onboard a property

Goal: create a clean operating record before adding tenants and leases.

Steps:

1. Collect address, city, apartment, municipal account if relevant, owner reference, and notes.
2. Create the property.
3. Review normalized spelling of city and street.
4. Add a recurring inspection reminder outside rent charges if needed.
5. Confirm access control to the JSON store.

Command:

```bash
property-management-scheduler property-add --address "הירקון 12" --city "תל אביב-יפו" --apartment "8" --store ./demo.json --env sandbox
```

Exit criteria:

- Property id exists.
- Address is readable in Hebrew.
- No tenant data was stored before consent or operational need.

## Workflow 2: Add tenant and create lease

Steps:

1. Add the tenant with preferred channel.
2. Validate email or Israeli phone format.
3. Create the lease with DD/MM/YYYY dates.
4. Set due day between 1 and 28.
5. Store deposit separately from rent.

Python:

```python
tenant = client.add_tenant(prop["id"], "דנה כהן", email="dana@example.com")
lease = client.create_lease(prop["id"], tenant["id"], "01/01/2026", "31/12/2026", "5200", due_day=5, deposit_ils="10400")
```

Exit criteria:

- Lease id exists.
- Monthly rent is stored with two decimal places.
- Deposit appears in the lease, not as a rent charge.

## Workflow 3: Generate rent charges

Steps:

1. Choose the start month.
2. Generate 1 to 36 monthly charges.
3. Review skipped duplicates.
4. Confirm charges stop at lease end date.
5. Save the JSON store.

Python:

```python
charges = client.schedule_rent(lease["id"], "01/01/2026", months=12)
```

Exit criteria:

- One charge per month exists.
- Due dates use the configured due day.
- No duplicate charges exist for the same lease and due date.

## Workflow 4: Collect rent and send reminders

Steps:

1. Build the daily agenda.
2. Review due and overdue charges.
3. Generate the rent reminder.
4. Confirm amount and date.
5. Send through the tenant preferred channel.
6. Log the communication.
7. Record payment when received.

Python:

```python
agenda = client.build_daily_agenda("05/01/2026")
message = client.generate_tenant_message("rent_reminder", charge_id=charge["id"])
client.log_communication(tenant["id"], prop["id"], "email", message["subject"], message["body"])
client.record_payment(charge["id"], "03/01/2026", "5200", reference="bank-2026-001")
```

Decision points:

- Partial amount: mark partial and follow up on the balance.
- No payment after grace period: mark overdue and document the next contact.
- Dispute: stop automation and escalate.

## Workflow 5: Maintenance triage

Steps:

1. Copy the tenant report into the description.
2. Let automatic priority suggest low, medium, high, or urgent.
3. Override priority if safety risk exists.
4. Add contractor and due date.
5. Update tenant with status.
6. Mark completed only after evidence or confirmation.

Python:

```python
task = client.create_maintenance(prop["id"], "נזילה", "מים יוצאים מתחת לכיור", due_date="15/02/2026")
client.update_maintenance_status(task["id"], "scheduled")
message = client.generate_tenant_message("maintenance_update", task_id=task["id"])
```

Exit criteria:

- Task severity matches risk.
- Entry to the unit is coordinated.
- Repair cost is kept separate from rent.

## Workflow 6: Lease renewal

Steps:

1. Search for leases ending within 60 days.
2. Generate a renewal check message.
3. Avoid presenting final terms before owner approval.
4. Log tenant response.
5. Create a new lease only after written confirmation.

Python:

```python
message = client.generate_tenant_message("lease_renewal", tenant_id=tenant["id"])
client.log_communication(tenant["id"], prop["id"], "email", message["subject"], message["body"], scheduled_for="01/11/2026")
```

## Workflow 7: Accounting preparation

Steps:

1. Reconcile all paid charges with references.
2. Export the accounting pack for the period.
3. Separate residential rent, commercial rent, repairs, reimbursements, and deposits.
4. Give the pack to the accountant or approved accounting system.
5. Keep official tax documents outside this scheduler unless an approved integration exists.

Python:

```python
pack = client.export_accounting_pack("01/01/2026", "31/01/2026")
```

Exit criteria:

- Paid rent total equals bank reconciliation.
- Open maintenance tasks are visible.
- Notes identify items requiring professional review.

## Workflow 8: Monthly review

Steps:

1. Run overdue report through daily agenda for the last day of the month.
2. Check open maintenance by priority.
3. Export accounting pack.
4. Back up the JSON store.
5. Review messages that failed delivery.
6. Prepare owner summary if managing for others.

## Workflow 9: Emergency handling

Steps:

1. Stop normal prioritization when the report mentions gas, fire, electricity, flood, sewage, or lockout.
2. Create an urgent maintenance task.
3. Contact emergency contractor or relevant authority.
4. Notify the tenant with practical coordination details.
5. Preserve records for insurance and professional review.

Do not automate safety decisions that require a licensed professional.


## Workflow 8: Check validated Israeli reference values

1. Run `property-management-scheduler reference-values --as-of 01/06/2026`.
2. Confirm the VAT reference, Israel Invoices threshold, and Bank of Israel API base.
3. Use the result as an accounting handoff note only.
4. Re-check official sources before production invoice handling.
