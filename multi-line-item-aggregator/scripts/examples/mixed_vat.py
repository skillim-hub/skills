from __future__ import annotations
import argparse, json, os
from multi_line_item_aggregator import CalculationOptions, Discount, aggregate_invoice

def parse_args():
    parser=argparse.ArgumentParser()
    parser.add_argument('--env', choices=['sandbox','production'], default=os.getenv('AGGREGATOR_ENV','sandbox'))
    parser.add_argument('--invoice-id', default=os.getenv('INVOICE_ID','SAMPLE-MIXED-VAT'))
    parser.add_argument('--invoice-date', default=os.getenv('INVOICE_DATE','15/06/2026'))
    parser.add_argument('--vat-number', default=os.getenv('VAT_NUMBER','515555555'))
    return parser.parse_args()

def main():
    args=parse_args()
    lines=[{'sku': 'LOCAL', 'description': 'Taxable service', 'quantity': '1', 'unit_price': '1000', 'vat_rate': '18%'}, {'sku': 'ZERO', 'description': 'Zero-rated item', 'quantity': '1', 'unit_price': '500', 'vat_rate': '0%'}]
    invoice_discount=None
    result=aggregate_invoice(lines, invoice_id=args.invoice_id, invoice_date=args.invoice_date, vat_number=args.vat_number, invoice_discount=invoice_discount, options=CalculationOptions(environment=args.env))
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
if __name__ == '__main__': main()
