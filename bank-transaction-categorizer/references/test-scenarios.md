# Test Scenarios

| # | Scenario | Input | Expected |
|---:|---|---|---|
| 1 | VAT payment | מע"מ תקופתי debit ₪1,200 | Taxes & Government / VAT |
| 2 | Income tax advance | מקדמות מס הכנסה debit ₪2,000 | Taxes & Government / Income tax |
| 3 | National Insurance | ביטוח לאומי debit ₪780 | Taxes & Government |
| 4 | Municipal tax | ארנונה עיריית תל אביב debit ₪640 | Municipal tax |
| 5 | Client transfer | העברה מלקוח חשבונית 1042 credit ₪3,500 | Income; confirm business income |
| 6 | Card settlement credit | זיכוי ישראכרט סליקה credit ₪8,200 | Income / Card settlement |
| 7 | Aggregate card debit | ישראכרט 02/2026 debit ₪4,100 | Credit Card Settlement |
| 8 | Bank fee | עמלת מסלול עסקים debit ₪29.90 | Bank Fees & Interest |
| 9 | Overdraft interest | ריבית חובה debit ₪45 | Bank Fees & Interest |
| 10 | Software subscription | ADOBE CREATIVE CLOUD debit ₪88 | Software & Cloud |
| 11 | Cloud provider | AWS EMEA debit ₪240 | Software & Cloud |
| 12 | Phone provider | סלקום עסקים debit ₪119 | Communications / partial |
| 13 | Internet provider | בזק בינלאומי debit ₪129 | Communications / partial |
| 14 | Fuel | פז תחנת דלק debit ₪350 | Travel & Fuel |
| 15 | Restaurant | WOLT debit ₪96 | Food & Meals / review |
| 16 | Supermarket | שופרסל דיל debit ₪420 | Personal/Review |
| 17 | Office rent | דמי שכירות משרד debit ₪5,000 | Rent & Facilities |
| 18 | Accountant | רואה חשבון כהן debit ₪950 | Professional Services |
| 19 | Attorney | עו"ד לוי debit ₪1,500 | Professional Services |
| 20 | Marketing | Google Ads debit ₪1,200 | Marketing & Advertising |
| 21 | Equipment | KSP מחשב נייד debit ₪4,800 | Equipment & Office |
| 22 | Cash withdrawal | משיכת מזומן כספומט debit ₪1,000 | Cash Withdrawals |
| 23 | BIT unknown credit | BIT העברה credit ₪250 | Wallet/Income with confirmation |
| 24 | PayBox debit | PayBox תשלום debit ₪90 | Transfers & Wallets |
| 25 | Refund | זיכוי ADOBE credit ₪88 | Preserve credit; review offset |
| 26 | Duplicate | Two identical date/description/amount rows | possible-duplicate |
| 27 | Missing date | Blank date | Validation error |
| 28 | Missing amount | No amount and no debit/credit | Validation error |
| 29 | Windows-1255 CSV | Older Hebrew export | Correct decoding |
| 30 | Mixed decimal formats | ₪1,234.56 / 1.234,56 / 123,45 | Correct Decimal values |
| 31 | Foreign merchant | MICROSOFT*AZURE debit | Software & Cloud |
| 32 | Loan repayment | החזר הלוואה debit | Loans & Financing |
| 33 | Salary expense | משכורת ינואר debit | Payroll & Benefits |
| 34 | Custom client rule | לקוח קבוע בע"מ credit | Custom rule wins |
| 35 | Blank rows | Empty lines in CSV | Ignore or report cleanly |
