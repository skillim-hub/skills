# Document workflows and templates

## Trademark filing packet

Create one folder per mark:

```text
TM_<MARK>_<DD/MM/YYYY>/
  01_applicant-details.md
  02_mark-details.md
  03_goods-services.md
  04_search-log.md
  05_risk-notes.md
  06_filing-receipt/
  07_office-actions/
  08_evidence-of-use/
```

### Applicant details

```markdown
# Applicant details

Legal name:
Applicant type:
ID/company number:
Country:
Address:
Email:
Phone:
Representative:
Ownership notes:
```

### Mark details

```markdown
# Mark details

Exact mark:
Mark type:
Language/script:
Translation:
Transliteration:
Meaning:
Logo/stylized file:
Color claim:
Disclaimed matter:
First use in Israel:
First use abroad:
Priority claim:
```

### Goods/services

```markdown
# Goods and services

| Class | Filing wording | Real use evidence | Notes |
|---|---|---|---|
| 43 | café services; restaurant services | photos, receipts | Active since 15/03/2026 |
```

### Search log

```markdown
# Search log

| Date | Source | Query | Relevant results | Risk |
|---|---|---|---|---|
| 20/05/2026 | Israel trademark database | NUNA | none close | Low |
```

## Patent filing packet

```text
PAT_<TITLE>_<DD/MM/YYYY>/
  01_confidentiality-warning.md
  02_invention-disclosure.md
  03_ownership.md
  04_prior-art-search.md
  05_drawings/
  06_draft-specification/
  07_attorney-review/
  08_filing-receipt/
  09_office-actions/
```

### Invention disclosure

```markdown
# Invention disclosure

Title:
Inventors:
Applicant/owner:
Technical field:
Problem:
Existing solutions:
Detailed solution:
Novel features:
Advantages:
Alternative embodiments:
Prototype status:
Test data:
Public disclosures:
Planned disclosures:
Commercial countries:
```

### Ownership review

```markdown
# Ownership review

Inventor employment status:
Contractor/client agreements:
University/hospital/funding obligations:
Founder assignment:
Open-source contributions:
Required assignments:
Risk level:
```

### Prior-art search

```markdown
# Prior-art search

| Date | Source | Query | Result/publication | Relevant feature | Difference |
|---|---|---|---|---|---|
| 20/05/2026 | Google Patents | pressure controlled irrigation valve | US... | sensor-controlled valve | lacks zone threshold table |
```

## Office action response packet

```text
OA_<APPLICATION>_<DD/MM/YYYY>/
  01_office-action.pdf
  02_deadline.md
  03_issue-table.md
  04_evidence/
  05_response-draft.md
  06_submitted-response/
```

### Issue table

```markdown
# Issue table

| Issue | Official wording | Response strategy | Evidence | Owner |
|---|---|---|---|---|
| Descriptiveness | mark describes service | argue acquired distinctiveness or rebrand | invoices, ads | applicant |
```

## Evidence packet

```text
EVIDENCE_<MARK>_<DD/MM/YYYY>/
  invoices/
  advertising/
  website-screenshots/
  social-media/
  packaging/
  media-coverage/
  declarations/
  summary.md
```

### Evidence summary

```markdown
# Evidence summary

Mark:
Period of use:
Geographic scope:
Sales revenue in ₪:
Advertising spend in ₪:
Customer count:
Channels:
Representative exhibits:
```

## Filename and quality rules

- Use English letters, numbers, hyphens, and underscores.
- Avoid slashes, quotes, emojis, and special characters.
- Use DD/MM/YYYY in Israeli-local folders.
- Keep original evidence files unchanged and work on copies.
- Confirm applicant name matches official records.
- Confirm mark text matches the filing form.
- Confirm patent drawings match reference numerals.
- Do not upload confidential patent material to public tools.
- Store payment confirmations and official receipts.
