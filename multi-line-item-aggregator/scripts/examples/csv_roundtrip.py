from __future__ import annotations
import argparse, csv, json, os, tempfile
from pathlib import Path
from multi_line_item_aggregator import CalculationOptions, aggregate_invoice, load_lines_from_csv

def parse_args():
    parser=argparse.ArgumentParser()
    parser.add_argument('--env', choices=['sandbox','production'], default=os.getenv('AGGREGATOR_ENV','sandbox'))
    parser.add_argument('--invoice-id', default=os.getenv('INVOICE_ID','SAMPLE-CSV'))
    parser.add_argument('--invoice-date', default=os.getenv('INVOICE_DATE','15/06/2026'))
    parser.add_argument('--vat-number', default=os.getenv('VAT_NUMBER','515555555'))
    return parser.parse_args()

def main():
    args=parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'invoice.csv'
        with path.open('w', newline='', encoding='utf-8') as handle:
            writer=csv.DictWriter(handle, fieldnames=['sku','description','quantity','unit_price','vat_rate'])
            writer.writeheader(); writer.writerow({'sku':'A','description':'שעת ייעוץ','quantity':'2','unit_price':'250','vat_rate':'18%'})
        result=aggregate_invoice(load_lines_from_csv(path), invoice_id=args.invoice_id, invoice_date=args.invoice_date, vat_number=args.vat_number, options=CalculationOptions(environment=args.env))
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
if __name__ == '__main__': main()
