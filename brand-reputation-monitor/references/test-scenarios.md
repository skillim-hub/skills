# Test Scenarios

Use these scenarios to validate Hebrew matching, sentiment, urgency, privacy redaction, and operational routing.

| # | Input | Source | Expected sentiment | Expected topic | Expected action |
|---:|---|---|---|---|---|
| 1 | `שירות מצוין, תודה רבה לדנה` | facebook | positive | service | thank or log praise |
| 2 | `לא להתקרב, חיכיתי שעה ואף אחד לא ענה` | x | negative | support | reply or route to support |
| 3 | `המוצר טוב אבל השירות איטי` | review | mixed | service | balanced reply |
| 4 | `מישהו יודע מה שעות הפתיחה?` | facebook | neutral | info | answer question |
| 5 | `קיבלתי חיוב כפול ואין מענה` | facebook | negative | billing | escalate to billing |
| 6 | `העוגה הייתה מקולקלת, הילד הקיא` | tiktok | urgent | safety | immediate escalation |
| 7 | `איזה שירות "מדהים", מחכה כבר יומיים` | x | negative | support | detect sarcasm |
| 8 | `אמאלה איזה טעים, נחזור שוב` | tiktok | positive | product | log praise |
| 9 | `הקופון לא עובד וזה מבאס` | tiktok | negative | campaign | fix coupon |
| 10 | `אני פונה לעורך דין אם לא תקבלו אחריות` | facebook | urgent | legal | preserve evidence |
| 11 | `המתחרים יותר זולים` | news_comment | neutral | pricing | competitive note |
| 12 | `לא קיבלתי חשבונית מס` | review | negative | billing | accounting review |
| 13 | `מספר הטלפון שלי 050-1234567, תחזרו אליי` | facebook | neutral | support | redact phone |
| 14 | `שלחתי מייל ל-a@example.com ולא ענו` | x | negative | support | redact email |
| 15 | `ת"ז 123456782 הופיעה בחשבונית` | facebook | urgent | privacy | redact ID and escalate |
| 16 | `המשלוח איחר אבל פיצו אותנו יפה` | review | mixed | delivery | log recovery |
| 17 | `משרד הבריאות צריך לבדוק את המקום הזה` | news_comment | urgent | safety | management review |
| 18 | `המחיר 120 ₪ היה שווה כל שקל` | review | positive | pricing | log praise |
| 19 | `יקר מדי ולא שווה` | tiktok | negative | pricing | review value perception |
| 20 | `הסטודיו של נועה מקצועי ונעים` | facebook | positive | service | thank |
| 21 | `נועה אחרת לגמרי, לא קשור לעסק` | facebook | neutral | false_positive | exclude without co-signal |
| 22 | `הייתה בעיית משלוח ב-24/06/2026` | support_export | negative | delivery | route to operations |
| 23 | `וואו מושלם!!!` | tiktok | positive | product | low-context praise |
| 24 | `החזר כספי לא הגיע כבר חודש` | facebook | negative | billing | billing escalation |
| 25 | `פרסמו מחיר בלי מע״מ? זה מטעה` | news_comment | urgent | consumer_protection | review ad/pricing |
| 26 | `התגובה של העובד הייתה משפילה` | review | negative | staff | manager review |
| 27 | `היה תור ארוך אבל הצוות היה אדיב` | review | mixed | queue | operational review |
| 28 | `ראיתי כתבה עליהם בחדשות` | facebook | urgent | media | manual review |
| 29 | `אין מלאי למרות הפרסום` | tiktok | negative | campaign | update inventory copy |
| 30 | `האתר לא נגיש לקורא מסך` | x | negative | accessibility | accessibility review |
| 31 | `הם רמאים וגנבים` | facebook | urgent | legal | avoid argument; preserve evidence |
| 32 | `אפשר לקבל קבלה על 80 ₪?` | facebook | neutral | billing | support answer |
| 33 | `הקליניקה שמרה על פרטיות בצורה מעולה` | review | positive | privacy | log praise |
| 34 | `פרטים רפואיים שלי נחשפו בקבלה` | facebook | urgent | privacy | privacy escalation |
| 35 | `לא רע בכלל` | review | positive | product | handle negation |
| 36 | `לא טוב בכלל` | review | negative | product | handle negation |
| 37 | `השליח היה אדיב אבל הגיע קר` | review | mixed | delivery | review courier flow |
| 38 | `המבצע נגמר לפני התאריך בפרסום` | facebook | negative | campaign | review ad terms |
| 39 | `העובדת בסניף חיפה הייתה מקצועית מאוד` | review | positive | staff | thank branch |
| 40 | `יש אפליה בשירות, לא נתנו לי להיכנס` | x | urgent | legal | management review |

## Execution template

1. Normalize text.
2. Detect source.
3. Redact personal data.
4. Classify sentiment.
5. Extract topics.
6. Compute risk.
7. Assign action.
8. Compare with expected.
9. Record human-review requirement.

## Acceptance criteria

- 90%+ accuracy on clear positive/negative/neutral examples.
- 100% redaction for simple emails, phone numbers, and Israeli ID-like patterns in this table.
- 100% urgent detection for safety, privacy, legal, regulator, and media scenarios.
- Human review for sarcasm, screenshots, missing thread context, and viral claims.
