# Test Scenarios

Run these scenarios before production and after every routing rule change. Expected outputs describe the key assertions, not every field.

## 1. Hebrew installation lead in Haifa

```json
{"name":"דנה","phone":"0521234567","message":"צריכה הצעת מחיר להתקנה באזור חיפה","channel":"whatsapp"}
```

Expected: `HE`, `HAIFA`, `installation`, department `installation`, priority `high`.

## 2. Hebrew sales lead in Tel Aviv

```json
{"phone":"0501112222","message":"אשמח למחיר בתל אביב","channel":"web_form"}
```

Expected: `HE`, `CENTER`, `sales`.

## 3. Hebrew billing request

```json
{"email":"noam@example.co.il","message":"אפשר לקבל חשבונית מס קבלה?"}
```

Expected: product `billing`, department `billing`.

## 4. Hebrew appointment request in Jerusalem

```json
{"phone":"025555555","message":"מבקשת לקבוע תור בירושלים"}
```

Expected: region `JERUSALEM`, product `appointments`.

## 5. Hebrew urgent support

```json
{"phone":"0521234567","message":"דחוף, השירות לא עובד עכשיו"}
```

Expected: product `support`, priority `urgent`, SLA 10 minutes.

## 6. English enterprise lead

```json
{"email":"ops@example.co.il","message":"Need rollout for 12 branches across Israel","budget":120000}
```

Expected: language `EN`, product `enterprise`, assignee `Enterprise Desk`.

## 7. English installation in Raanana

```json
{"email":"lead@example.com","message":"Need pricing for installation in Raanana"}
```

Expected: language `EN`, region `SHARON`, product `installation`.

## 8. Russian support in Haifa

```json
{"phone":"+972541112222","city":"חיפה","message":"Устройство не работает, нужна помощь"}
```

Expected: language `RU`, product `support`, assignee `Russian Support Queue`.

## 9. Russian sales without region

```json
{"phone":"0521234567","message":"Нужна цена на услугу"}
```

Expected: language `RU`, product `sales`, warning `UNKNOWN_REGION`.

## 10. Arabic sales in Nazareth

```json
{"phone":"0523334444","city":"נצרת","message":"مرحبا، أريد عرض سعر للخدمة"}
```

Expected: language `AR`, region `NORTH`, product `sales`, assignee `Arabic Sales Queue`.

## 11. Arabic urgent support

```json
{"phone":"0523334444","message":"طارئ، الخدمة لا تعمل"}
```

Expected: language `AR`, priority `urgent`, Arabic or multilingual support path.

## 12. Mixed English and Hebrew

```json
{"phone":"0521234567","message":"Hi, צריך עזרה בהתקנה ברמת גן"}
```

Expected: language `HE`, warning `LANGUAGE_MIXED`, region `CENTER`.

## 13. Explicit language override

```json
{"phone":"0521234567","language":"ru","message":"Need help with invoice"}
```

Expected: language `RU`, product `billing`.

## 14. City beats phone area code

```json
{"phone":"03-5555555","city":"באר שבע","message":"צריך התקנה"}
```

Expected: region `SOUTH`, not `CENTER`.

## 15. Area code fallback

```json
{"phone":"02-5555555","message":"צריך תור"}
```

Expected: region `JERUSALEM` with `REGION_FROM_PHONE_WEAK`.

## 16. Mobile phone does not infer region

```json
{"phone":"052-1234567","message":"צריך מחיר"}
```

Expected: region `UNKNOWN`.

## 17. Missing contact

```json
{"message":"אשמח להצעת מחיר"}
```

Expected: assignee `Data Quality Queue`, warning `MISSING_CONTACT`.

## 18. Invalid phone with email

```json
{"phone":"abc","email":"lead@example.co.il","message":"Need pricing"}
```

Expected: warning `PHONE_INVALID`, route still succeeds using email.

## 19. Missing marketing consent

```json
{"phone":"0521234567","message":"אשמח להצעת מחיר","consent_marketing":false}
```

Expected: warning `MARKETING_CONSENT_MISSING`.

## 20. Unknown language

```json
{"phone":"0521234567","message":"Necesito precio para instalación"}
```

Expected: language `UNKNOWN`, warning `UNSUPPORTED_LANGUAGE`, multilingual intake or qualification.

## 21. Eilat installation

```json
{"phone":"0521234567","city":"אילת","message":"צריך התקנה"}
```

Expected: region `EILAT`, installation route.

## 22. West Bank locality

```json
{"phone":"0521234567","city":"אריאל","message":"מבקש הצעת מחיר"}
```

Expected: region `WEST_BANK`, product `sales`.

## 23. Budget upgrades priority

```json
{"email":"buyer@example.co.il","message":"Need quote","budget":60000}
```

Expected: priority `high`, senior sales route.

## 24. Billing in Russian

```json
{"email":"client@example.co.il","message":"Нужен счет за оплату"}
```

Expected: language `RU`, product `billing`.

## 25. Arabic billing

```json
{"email":"client@example.co.il","message":"أحتاج فاتورة للدفع"}
```

Expected: language `AR`, product `billing`.

## 26. Unknown product with known city

```json
{"phone":"0521234567","city":"חדרה","message":"שלום, אפשר פרטים?"}
```

Expected: region `SHARON`, product `general`, qualification route.

## 27. WhatsApp hot sales

```json
{"phone":"0521234567","message":"אפשר מחיר היום ברמת גן?","channel":"whatsapp"}
```

Expected: priority `high`, not necessarily `urgent`.

## 28. Enterprise Hebrew

```json
{"email":"ops@example.co.il","message":"צריכים פריסה ארצית ל-10 סניפים","budget":90000}
```

Expected: product `enterprise`, assignee `Enterprise Desk`.

## 29. Duplicate risk supplied externally

```json
{"phone":"0521234567","message":"צריך מחיר","metadata":{"duplicate_risk":true}}
```

Expected: warning `DUPLICATE_RISK`.

## 30. Unsupported but contactable lead

```json
{"phone":"+972521234567","message":"Bonjour, besoin de prix"}
```

Expected: route not discarded; multilingual intake or qualification.
