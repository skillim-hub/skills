from __future__ import annotations
import asyncio, csv, json
from decimal import Decimal
import pytest
from click.testing import CliRunner
from multi_line_item_aggregator import AggregatorError, CalculationOptions, Discount, DiscountAllocationMethod, DiscountType, InvoiceLine, aggregate_invoice, aggregate_invoice_async, allocate_discount, create_sample_invoice, format_summary, load_lines_from_csv, load_lines_from_json, normalize_rate, parse_decimal, parse_discount, save_result_json
from multi_line_item_aggregator.cli import app

def line(**overrides):
    base={'sku':'A','description':'Item','quantity':'2','unit_price':'100','vat_rate':'18%'}; base.update(overrides); return InvoiceLine.from_mapping(base)
def aggregate(*lines, **kwargs): return aggregate_invoice(list(lines), **kwargs)
def test_parse_decimal_money_symbol(): assert parse_decimal('₪1,234.50') == Decimal('1234.50')
def test_normalize_percent_string(): assert normalize_rate('18%') == Decimal('0.18')
def test_normalize_whole_percent_number(): assert normalize_rate('18') == Decimal('0.18')
def test_basic_single_line_total():
    r=aggregate(line(quantity='1', unit_price='100')); assert r.totals.taxable_total==Decimal('100.00'); assert r.totals.vat_total==Decimal('18.00'); assert r.totals.grand_total==Decimal('118.00')
def test_quantity_decimal(): assert aggregate(line(quantity='1.5', unit_price='80')).totals.taxable_total == Decimal('120.00')
def test_line_percent_discount():
    r=aggregate(line(quantity='1', unit_price='100', discount_type='percent', discount_value='10')); assert r.totals.line_discounts_total==Decimal('10.00'); assert r.totals.taxable_total==Decimal('90.00')
def test_line_amount_discount():
    r=aggregate(line(quantity='1', unit_price='100', discount_type='amount', discount_value='15')); assert r.totals.line_discounts_total==Decimal('15.00'); assert r.totals.taxable_total==Decimal('85.00')
def test_invoice_percent_discount():
    r=aggregate(line(quantity='1', unit_price='100'), invoice_discount=Discount.percent('10')); assert r.totals.invoice_discount_total==Decimal('10.00'); assert r.totals.taxable_total==Decimal('90.00')
def test_invoice_amount_discount_two_lines_allocates_to_sum():
    r=aggregate(line(sku='A', quantity='1', unit_price='100'), line(sku='B', quantity='1', unit_price='50'), invoice_discount=Discount.amount('15')); assert sum((ln.invoice_discount_share for ln in r.lines), Decimal('0')) == Decimal('15.00')
def test_equal_allocation():
    r=aggregate(line(sku='A', quantity='1', unit_price='100'), line(sku='B', quantity='1', unit_price='300'), invoice_discount=Discount.amount('20'), options=CalculationOptions(invoice_discount_allocation=DiscountAllocationMethod.EQUAL)); assert [ln.invoice_discount_share for ln in r.lines] == [Decimal('10.00'), Decimal('10.00')]
def test_zero_vat_line():
    r=aggregate(line(quantity='1', unit_price='100', vat_rate='0%')); assert r.totals.vat_total==Decimal('0.00'); assert r.totals.grand_total==Decimal('100.00')
def test_mixed_vat_rates():
    r=aggregate(line(sku='A', quantity='1', unit_price='100', vat_rate='18%'), line(sku='B', quantity='1', unit_price='100', vat_rate='0%')); assert r.totals.vat_total==Decimal('18.00'); assert r.totals.grand_total==Decimal('218.00')
def test_fractional_agorot_rounding():
    r=aggregate(line(quantity='1', unit_price='0.05', vat_rate='18%')); assert r.lines[0].vat_amount==Decimal('0.01'); assert r.lines[0].fractional_agorot_vat==Decimal('-0.0010')
def test_to_dict_strings_decimals(): assert aggregate(line(quantity='1', unit_price='100')).to_dict()['totals']['grand_total'] == '118.00'
def test_to_json_contains_invoice_id(): assert '"invoice_id": "INV-1"' in aggregate(line(quantity='1', unit_price='100'), invoice_id='INV-1').to_json()
def test_negative_rejected_by_default():
    with pytest.raises(AggregatorError): aggregate(line(quantity='-1', unit_price='100'))
def test_negative_allowed_option(): assert aggregate(line(quantity='-1', unit_price='100'), options=CalculationOptions(allow_negative_lines=True)).totals.subtotal_before_discounts == Decimal('-100.00')
def test_zero_quantity_rejected_by_default():
    with pytest.raises(AggregatorError): aggregate(line(quantity='0', unit_price='100'))
def test_zero_quantity_allowed(): assert aggregate(line(quantity='0', unit_price='100'), options=CalculationOptions(allow_zero_quantity=True)).totals.grand_total == Decimal('0.00')
def test_discount_exceeding_line_rejected():
    with pytest.raises(AggregatorError): aggregate(line(quantity='1', unit_price='100', discount_type='amount', discount_value='101'))
def test_percent_discount_over_100_rejected():
    with pytest.raises(AggregatorError): aggregate(line(quantity='1', unit_price='100', discount_type='percent', discount_value='101'))
def test_invoice_discount_exceeding_base_rejected():
    with pytest.raises(AggregatorError): aggregate(line(quantity='1', unit_price='100'), invoice_discount=Discount.amount('101'))
def test_empty_lines_rejected():
    with pytest.raises(AggregatorError): aggregate_invoice([])
def test_async_wrapper(): assert asyncio.run(aggregate_invoice_async([line(quantity='1', unit_price='100')])).totals.grand_total == Decimal('118.00')
def test_load_json_list(tmp_path):
    p=tmp_path/'lines.json'; p.write_text(json.dumps([{'sku':'A','description':'A','quantity':'1','unit_price':'100','vat_rate':'18%'}]), encoding='utf-8'); assert len(load_lines_from_json(p)) == 1
def test_load_json_object(tmp_path):
    p=tmp_path/'invoice.json'; p.write_text(json.dumps({'lines':[{'sku':'A','description':'A','quantity':'1','unit_price':'100','vat_rate':'18%'}]}), encoding='utf-8'); assert len(load_lines_from_json(p)) == 1
def test_load_csv(tmp_path):
    p=tmp_path/'lines.csv'
    with p.open('w', newline='', encoding='utf-8') as h:
        w=csv.DictWriter(h, fieldnames=['sku','description','quantity','unit_price','vat_rate']); w.writeheader(); w.writerow({'sku':'A','description':'A','quantity':'1','unit_price':'100','vat_rate':'18%'})
    assert len(load_lines_from_csv(p)) == 1
def test_save_result_json(tmp_path):
    p=tmp_path/'out.json'; save_result_json(aggregate(line(quantity='1', unit_price='100')), p); assert json.loads(p.read_text(encoding='utf-8'))['totals']['grand_total'] == '118.00'
def test_format_summary(): assert 'Grand total: 118.00' in format_summary(aggregate(line(quantity='1', unit_price='100'), invoice_id='INV'))
def test_parse_discount_none(): assert parse_discount(None, None) is None
def test_parse_discount_amount():
    d=parse_discount('amount','5'); assert d.type == DiscountType.AMOUNT; assert d.value == Decimal('5')
def test_allocate_rounding_delta_exact_total(): assert sum(allocate_discount([Decimal('0.01'), Decimal('0.01'), Decimal('0.01')], Decimal('0.01'))) == Decimal('0.01')
def test_create_sample_invoice_response(tmp_path):
    p=tmp_path/'sample.json'; resp=create_sample_invoice(p, environment='sandbox'); assert resp['id']=='SAMPLE-2026-0001'; assert json.loads(p.read_text(encoding='utf-8'))['id']=='SAMPLE-2026-0001'
def test_cli_create_sample_and_aggregate_chain(tmp_path):
    runner=CliRunner(); p=tmp_path/'sample.json'; cr=runner.invoke(app, ['create-sample','--env','sandbox',str(p)]); assert cr.exit_code==0; created=json.loads(cr.output); ar=runner.invoke(app, ['aggregate',str(p),'--env','sandbox','--id',created['id'],'--json-output']); assert ar.exit_code==0; assert json.loads(ar.output)['invoice_id'] == created['id']
def test_invalid_environment_rejected():
    with pytest.raises(AggregatorError): aggregate_invoice([line(quantity='1', unit_price='100')], options=CalculationOptions(environment='qa'))


def test_default_vat_rate_web_validated_2026():
    import multi_line_item_aggregator as pkg
    assert pkg.__version__ == "2.2.0"
    assert pkg.DEFAULT_VAT_RATE == Decimal("0.18")


def test_no_webhook_features_exposed():
    import multi_line_item_aggregator as pkg
    assert not any("webhook" in name.lower() for name in pkg.__all__)
