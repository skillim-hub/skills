# Troubleshooting

## Too many false positives

Causes: brand name is a common first name, generic product terms, no co-occurrence rules, competitor names, old hashtags.

Fix:

- Require two signals for common names: name + product, city, domain, phone, branch, or campaign.
- Add negative keywords.
- Separate owner-name monitoring from brand-name monitoring.
- Sample top 50 false positives and create rules.
- Lower confidence on generic matches.

Example:

```text
Bad: דנה
Better: ("המאפייה של דנה" OR "Dana Bakery" OR ("דנה" AND ("עוגת שמרים" OR "רחוב הרצל")))
```

## Missing Hebrew mentions

Causes: missing spelling variants, prefixes attached to brand name, English spelling, nickname, hashtag, export pagination, encoding issue.

Fix:

1. Add variants with prefixes.
2. Add misspellings.
3. Add product/service names.
4. Inspect raw export row count.
5. Confirm UTF-8.
6. Test known examples.

## Sentiment too positive

Causes: sarcasm, positive word inside complaint, negation ignored, quote marks.

Fix: Treat `"מדהים"` with complaint words as negative; strengthen `אבל`, `רק חבל`, `למרות`, `חיכיתי`, `לא עונים`; add overrides for `לא מומלץ`, `לא להתקרב`, `אין מענה`.

## Sentiment too negative

Causes: slang interpreted literally, complaint about competitor, question about refund, recovery story.

Fix: Add slang positives: `אמאלה`, `וואו`, `נדיר`, `מושלם`; detect `אבל טיפלו`, `בסוף הסתדר`, `פיצו אותנו`; identify target before final sentiment.

## Urgent item missed

Causes: missing domain term, engagement not used, news source not weighted, indirect language.

Fix: add sector terms, set per-source engagement thresholds, manual review for journalists/regulators, flag repeated similar complaints within 24 hours.

## Every legal mention is urgent

Causes: over-weighting `חוקי`, `זכויות`, `אחריות`.

Fix: keep `תביעה`, `עורך דין`, `מכתב התראה`, `משטרה`, `משרד הבריאות`, `הרשות להגנת הצרכן` as stronger; treat `אחריות` as medium unless paired with severe terms.

## CLI cannot read file

Check:

- Path exists.
- File is CSV, JSON, or JSONL.
- File is UTF-8.
- CSV has `text` column or pass `--text-field`.
- JSON is a list or object with `mentions`.

```bash
python scripts/brand-reputation-monitor-cli.py analyze data/comments.csv --text-field body
```

## Hebrew appears as gibberish

Cause: wrong encoding, often Windows-1255 or mixed spreadsheet export.

Fix: re-export as CSV UTF-8, then rerun. For repeated jobs, normalize encoding in collector.

## Duplicate mentions

Fix: deduplicate by URL, otherwise hash source + date + normalized text. Keep highest engagement. Mark cross-posts rather than deleting evidence from a different platform.

## Privacy risk in output

Fix: run redaction, show minimal excerpt, restrict raw exports, use aggregate owner reports, and remove personal details from screenshots before sharing.

## Poor performance

Fix: process JSONL/CSV in batches, avoid spreadsheet loading for huge files, cache normalized text, disable expensive fuzzy matching on first pass, keep only required fields.

## Escalate immediately when mention includes

- Injury, allergy, poisoning, unsafe product, contamination.
- Fraud, double charge with evidence, systematic billing failure.
- Privacy breach, leaked data, medical data, minors.
- Discrimination, harassment, threats.
- Journalist, news outlet, regulator, police, Ministry of Health, Consumer Protection Authority.
- Viral spread or influencer involvement.

Escalation template:

```text
Date: 24/06/2026
Source: TikTok
Risk: 82
Issue: Alleged food safety incident
Evidence: Public video URL and 3 comments
Status: Not yet verified
Immediate action: Management review and private customer contact
```
