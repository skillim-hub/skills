# Workflow guide

## Workflow 1: Freelancer tax glossary

Goal: Produce a practical glossary for an Israeli freelancer preparing onboarding or invoice instructions.

1. Collect terms from the invoice template, accountant checklist, and client onboarding message.
2. Set `industry="freelance"` and `audience="freelancer"`.
3. Normalize Hebrew and English duplicates such as `VAT`, `מע"מ`, and `מס ערך מוסף`.
4. Build the glossary in sandbox mode.
5. Verify Tax Authority terms and National Insurance terms before external publication.
6. Export Markdown for human review and JSON for reuse in systems.

Command:

```bash
tgb create "עוסק פטור" "עוסק מורשה" "ניכוי מס במקור" "דמי ביטוח לאומי" --industry freelance --env sandbox --store ./freelancer-store.json
```

## Workflow 2: Retail consumer glossary

Goal: Explain consumer-facing terms on a store website.

1. Set `industry="retail"` and `audience="consumer"`.
2. Include cancellation, warranty, VAT, price, and standard mark terms.
3. Cite the Consumer Protection and Fair Trade Authority for cancellation and warranty terms.
4. Cite the Tax Authority for VAT.
5. Cite the Standards Institution of Israel for standard mark terms.
6. Use plain Hebrew for public pages and avoid professional accounting jargon unless needed.

Command:

```bash
tgb build "Consumer cancellation" "Warranty certificate" "VAT" "Standard mark" --industry retail --format markdown
```

## Workflow 3: Privacy and accessibility website glossary

Goal: Create a glossary for a small business website policy folder.

1. Set `industry="privacy"` or `industry="web"`.
2. Include `Privacy policy`, `Database registration or notice`, and `Accessibility statement`.
3. Keep privacy and accessibility terms in separate sections when possible.
4. Cite the Privacy Protection Authority for privacy terms.
5. Cite the Commission for Equal Rights of Persons with Disabilities for accessibility statement terms.
6. Flag professional review before publishing policy pages.

Command:

```bash
tgb build "Privacy policy" "Database registration or notice" "Accessibility statement" --industry privacy --format json
```

## Workflow 4: Importer standards glossary

Goal: Help an importer distinguish tax, customs, product standard, and consumer terms.

1. Set `industry="import"` and `audience="small_business"`.
2. Include `Import declaration`, `Standard mark`, `VAT`, and any product-specific standards terms.
3. Cite Tax Authority customs resources for import declarations and import taxation.
4. Cite the Standards Institution of Israel for standards and standard mark.
5. Do not merge customs duties, VAT, and product safety obligations into one definition.
6. Add a review warning for product-specific terms not in the local term library.

## Workflow 5: Company onboarding glossary

Goal: Explain corporate and finance terms to a founder or operations manager.

1. Set `industry="corporate"`.
2. Include `Company extract`, `Private company`, `Prospectus` only when relevant.
3. Cite the Corporations Authority for company records.
4. Cite the Israel Securities Authority for securities disclosure terms.
5. Mark investment and securities terms for legal review.

## Human review workflow

Use this sequence before external publication:

```mermaid
flowchart LR
    A[Draft glossary] --> B[Source check]
    B --> C[Hebrew terminology check]
    C --> D[Date and ₪ check]
    D --> E[Professional review]
    E --> F[Publish]
```

Review checklist:

- Confirm every source supports the exact term.
- Confirm the Hebrew term is accepted in Israeli professional usage.
- Confirm no exact deadline, rate, or threshold is copied without a date.
- Confirm the glossary does not present advice as a final legal or accounting instruction.
- Confirm the same glossary id is used when chaining create and export commands.
