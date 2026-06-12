from __future__ import annotations
import argparse, json, os
from multi_line_item_aggregator import CalculationOptions, Discount, aggregate_invoice

def parse_args():
    parser=argparse.ArgumentParser()
    parser.add_argument('--env', choices=['sandbox','production'], default=os.getenv('AGGREGATOR_ENV','sandbox'))
    parser.add_argument('--invoice-id', default=os.getenv('INVOICE_ID','SAMPLE-BASIC'))
    parser.add_argument('--invoice-date', default=os.getenv('INVOICE_DATE','15/06/2026'))
    parser.add_argument('--vat-number', default=os.getenv('VAT_NUMBER','515555555'))
    return parser.parse_args()

def main():
    args=parse_args()
    lines=[{'sku': 'CONSULT', 'description': 'Consulting hour', 'quantity': '4', 'unit_price': '250', 'vat_rate': '18%'}, {'sku': 'TRAVEL', 'description': 'Travel reimbursement', 'quantity': '1', 'unit_price': '60', 'vat_rate': '18%'}]
    invoice_discount=None
    result=aggregate_invoice(lines, invoice_id=args.invoice_id, invoice_date=args.invoice_date, vat_number=args.vat_number, invoice_discount=invoice_discount, options=CalculationOptions(environment=args.env))
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
if __name__ == '__main__': main()
