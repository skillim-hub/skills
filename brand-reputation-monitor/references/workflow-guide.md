# Workflow Guide

## Workflow 1: First setup

1. List business identifiers: official Hebrew name, English name, spelling variants, owner/professional public name, product, campaign, phone, domain, branch, city.
2. Select permitted sources: Facebook public-page exports, X/Twitter approved search/export, TikTok approved export/vendor, review exports, news comments where permitted, support inbox extracts.
3. Define exclusions: same-name people, generic product words, competitors, old campaigns, irrelevant neighborhoods.
4. Define retention: routine mentions 6-12 months, aggregates 24 months, incidents per qualified advice.
5. Run calibration on historical data.
6. Tune false positives and false negatives.
7. Assign owners: support, operations, accounting, management, privacy/legal, marketing.
8. Create response templates.
9. Run 20+ test scenarios.
10. Launch with daily human review.

Deliverable: keyword map, source list, escalation matrix, retention rule, baseline report.

## Workflow 2: Daily monitoring

1. Import permitted exports.
2. Normalize dates to DD/MM/YYYY.
3. Normalize sources.
4. Redact unnecessary personal data.
5. Deduplicate by URL or normalized fingerprint.
6. Classify sentiment and topics.
7. Compute risk.
8. Manually review urgent and high-risk items.
9. Assign owner and due date.
10. Export response queue and owner summary.

Daily summary template:

```text
Date: 24/06/2026
New mentions: 37
Urgent: 1
Negative: 6
Top issue: delivery delays after 18:00
Action today: reply to 4 customers, check courier SLA, update estimated delivery copy.
```

## Workflow 3: Viral complaint

Triggers:

- Engagement above configured threshold.
- Influencer, journalist, regulator, or large group.
- Repeated claim from multiple users.
- Legal, safety, privacy, discrimination, fraud, or health language.

Steps:

1. Preserve URL, timestamp, source, and text.
2. Pause automated replies.
3. Identify factual claim and operational owner.
4. Check order, branch, staff shift, inventory, refund, invoice, delivery log, or safety record.
5. Draft short acknowledgement.
6. Move personal details to private channel.
7. Escalate to management and qualified advisor when required.
8. Publish follow-up only after fact-checking.
9. Document final outcome and process improvement.

Avoid: `זה לא נכון`, `את משקרת`, `נתבע אותך`, or public disclosure of customer data.

## Workflow 4: Campaign launch monitoring

Before launch:

- Add slogan, hashtag, landing page, coupon code, influencer handles.
- Add expected confusion points: price, VAT, stock, dates, branches, delivery areas.
- Prepare FAQ responses.
- Set review cadence every 2-4 hours on launch day.

During launch:

- Watch `קופון לא עובד`, `אין מלאי`, `יקר`, `הטעיה`, `אותיות קטנות`.
- Fix source of confusion before replying repeatedly.
- Summarize by channel and topic.

After launch:

- Compare sentiment by source.
- Identify repeated misunderstandings.
- Update landing page, FAQ, and campaign copy.
- Archive raw exports under retention rules.

## Workflow 5: Billing and accounting complaint

Trigger words: `חשבונית`, `קבלה`, `זיכוי`, `חיוב כפול`, `מע״מ`, `החזר`, `ביטול עסקה`.

Steps:

1. Mark topic `billing`.
2. Increase risk for double charge, missing refund, missing invoice, VAT confusion.
3. Do not discuss transaction details publicly.
4. Ask for order number privately.
5. Route to accounting/support.
6. Track due date.
7. Close only after billing owner confirms.

Reply:

```text
תודה שהעלית את זה. חיוב או מסמך חשבונאי לא ברור צריכים להיבדק מיד. נא לשלוח לנו בפרטי מספר הזמנה או חשבונית, ונחזור אליך עם תשובה מסודרת.
```

## Workflow 6: Food, health, or safety complaint

Trigger words: `הרעלה`, `אלרגיה`, `מסוכן`, `משרד הבריאות`, `עובש`, `מקולקל`, `פציעה`.

Steps:

1. Mark urgent.
2. Preserve evidence.
3. Do not debate publicly.
4. Ask privately for minimum required details.
5. Escalate to management.
6. Check batch, supplier, branch, cleaning log, staff, product date, and incident history.
7. Seek qualified review where needed.
8. Create incident report.

## Workflow 7: Freelancer monitoring

For consultants, designers, tutors, therapists, trainers, electricians, and similar solo businesses:

1. Monitor public name, business name, domain, phone, and niche phrase.
2. Avoid collecting client details.
3. Categorize availability, pricing, professionalism, results, scheduling, refunds.
4. Treat confidentiality complaints as urgent.
5. Use privacy-protective replies.

Template:

```text
תודה על הפנייה. כדי לשמור על פרטיות, עדיף להמשיך את הבדיקה בפרטי. אפשר לשלוח פרטים ונחזור אליך בהקדם.
```

## Workflow 8: Monthly improvement review

1. Export resolved mentions.
2. Group by topic, source, branch, weekday, and campaign.
3. Compare current month with previous month.
4. Find top preventable complaints.
5. Assign operational improvements.
6. Update templates, FAQ, and keyword map.
7. Remove obsolete keywords.
8. Document false positives and false negatives.

## Workflow 9: Human review loop

Use manual review when:

- Risk score is 50+.
- Sentiment is mixed with high engagement.
- Source context is incomplete.
- Mention involves minors, health, privacy, discrimination, fraud, legal threat, media, or regulator.
- Star rating conflicts with text.

Reviewer fields: `reviewer_decision`, `reviewer_action`, `owner`, `due_date`, `notes`, `status`.

## Workflow 10: Owner-ready report

Answer:

1. What happened?
2. Why does it matter?
3. What should be done today?
4. Which process should change?
5. Which items require caution?

Avoid model jargon and unnecessary personal data.
