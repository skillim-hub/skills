from __future__ import annotations

import argparse
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument("--env", choices=["sandbox", "production"], default=os.getenv("RTL_ADVISOR_ENV", "sandbox"))
args = parser.parse_args()

document = {
    "type": os.getenv("RTL_ADVISOR_DOC_TYPE", "חשבונית מס/קבלה"),
    "number": os.getenv("RTL_ADVISOR_DOC_NUMBER", "INV-2026-0042"),
    "date": os.getenv("RTL_ADVISOR_DOC_DATE", "03/06/2026"),
    "customer": os.getenv("RTL_ADVISOR_CUSTOMER", "דנה לוי"),
    "total": os.getenv("RTL_ADVISOR_TOTAL", "₪ 1,180.00"),
}
html = f"""<section lang="he" dir="rtl" class="invoice">
  <h1>{document["type"]}</h1>
  <p>מספר מסמך: <bdi dir="ltr">{document["number"]}</bdi></p>
  <p>תאריך: <bdi dir="ltr">{document["date"]}</bdi></p>
  <p>לקוח: <bdi dir="auto">{document["customer"]}</bdi></p>
  <p>סה"כ לתשלום: <bdi dir="ltr">{document["total"]}</bdi></p>
</section>"""
print(json.dumps({"env": args.env, "document": document, "html": html}, ensure_ascii=False, indent=2))
