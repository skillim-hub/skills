from __future__ import annotations
import asyncio, json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Mapping

class Language(str, Enum):
    EN='en'; HE='he'
class TaxTopic(str, Enum):
    VAT_REGISTRATION='vat-registration'; VAT_INVOICE_CORRECTION='vat-invoice-correction'; FOREIGN_CLIENT_VAT='foreign-client-vat'; EXPENSE_DEDUCTIBILITY='expense-deductibility'; WITHHOLDING_TAX='withholding-tax'; ANNUAL_RETURN='annual-return'; RENTAL_INCOME='rental-income'; REAL_ESTATE_SALE='real-estate-sale'; PURCHASE_TAX='purchase-tax'; INHERITANCE_APARTMENT='inheritance-apartment'
class Workflow(str, Enum):
    FREELANCER_ONBOARDING='freelancer-onboarding'; VAT_DOCUMENTS='vat-documents'; FOREIGN_CLIENT_VAT='foreign-client-vat'; EXPENSE_REVIEW='expense-review'; WITHHOLDING_CHECK='withholding-check'; ANNUAL_RETURN='annual-return'; RENTAL_INCOME='rental-income'; REAL_ESTATE_SALE='real-estate-sale'; PURCHASE_TAX='purchase-tax'; TAX_AUTHORITY_LETTER='tax-authority-letter'

@dataclass(frozen=True)
class ExplanationRequest:
    topic: str; user_type: str='unspecified'; facts: Mapping[str, Any]=field(default_factory=dict); language: str='en'
@dataclass(frozen=True)
class Explanation:
    topic: str; language: str; summary: str; decision_points: list[str]; documents: list[str]; warnings: list[str]; professional_help: bool; missing_facts: list[str]=field(default_factory=list); legal_areas: list[str]=field(default_factory=list)
    def to_dict(self)->dict[str, Any]: return asdict(self)
    def to_json(self, *, ensure_ascii: bool=False)->str: return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=2)
@dataclass(frozen=True)
class ValidationResult:
    valid: bool; missing: list[str]; warnings: list[str]
    def to_dict(self)->dict[str, Any]: return asdict(self)
class TaxLawExplainerError(ValueError): code='TAX_LAW_EXPLAINER_ERROR'
class UnknownTopicError(TaxLawExplainerError): code='UNKNOWN_TOPIC'
class UnknownWorkflowError(TaxLawExplainerError): code='UNKNOWN_WORKFLOW'
class InvalidLanguageError(TaxLawExplainerError): code='INVALID_LANGUAGE'

REQUIRED_FACTS = {
 'vat-registration':['activity_type','profession','annual_turnover','start_date'],
 'vat-invoice-correction':['vat_status','original_invoice','report_period','correction_reason'],
 'foreign-client-vat':['client_residence','beneficiary','use_location','contract'],
 'expense-deductibility':['expense_type','business_purpose','has_invoice'],
 'withholding-tax':['payer','payee','payment_type','certificate_valid'],
 'annual-return':['income_sources','tax_year','file_status'],
 'rental-income':['property_type','monthly_rent','owner_type'],
 'real-estate-sale':['asset_type','purchase_date','sale_date','purchase_price','sale_price','family_unit_holdings','construction_rights'],
 'purchase-tax':['asset_type','purchaser_status','owns_other_apartment','purchase_price'],
 'inheritance-apartment':['deceased_status','heir_status','asset_type','prior_holdings']}
LEGAL_AREAS = {
 'vat-registration':['VAT Law'], 'vat-invoice-correction':['VAT Law','VAT Regulations'], 'foreign-client-vat':['VAT Law'],
 'expense-deductibility':['Income Tax Ordinance','VAT Law'], 'withholding-tax':['Income Tax Ordinance','Income Tax Regulations'], 'annual-return':['Income Tax Ordinance'],
 'rental-income':['Income Tax Ordinance','VAT Law'], 'real-estate-sale':['Real Estate Taxation Law'], 'purchase-tax':['Real Estate Taxation Law'], 'inheritance-apartment':['Real Estate Taxation Law']}
DOCS = {
 'vat-registration':['Identity details','Bank account confirmation','Projected turnover support','Service contracts','Profession description'],
 'vat-invoice-correction':['Original invoice','Credit invoice or correction document','VAT report for affected period','Customer correspondence'],
 'foreign-client-vat':['Contract','Foreign client details','Statement of work','Proof of payment','Evidence of use outside Israel'],
 'expense-deductibility':['Tax invoice or receipt','Payment proof','Business-purpose memo','Allocation calculation for mixed use'],
 'withholding-tax':['Withholding certificate','Bookkeeping approval','Payment statement','Contract or purchase order'],
 'annual-return':['Form 106','Form 867','Withholding certificates','Expense records','Foreign statements if relevant'],
 'rental-income':['Lease agreement','Monthly rent schedule','Expense invoices','Mortgage interest support if relevant'],
 'real-estate-sale':['Purchase agreement','Sale agreement draft','Land registry extract','Purchase tax assessment','Improvement invoices','Municipal information'],
 'purchase-tax':['Purchase agreement draft','Purchaser residency support','Apartment holdings declaration','Price allocation if mixed asset'],
 'inheritance-apartment':['Inheritance order or probate order','Deceased apartment history','Heir apartment holdings','Sale agreement draft']}
SUMMARY_EN = {
 'vat-registration':'Check VAT status before issuing documents or collecting VAT.', 'vat-invoice-correction':'Correct VAT documents through a lawful matching correction path.', 'foreign-client-vat':'Analyze zero-rate VAT only after identifying the actual beneficiary and use location.', 'expense-deductibility':'Test business purpose, documentation, private use, and VAT restrictions separately.', 'withholding-tax':'Check certificate validity and payment type before accepting withholding.', 'annual-return':'Determine whether a return is mandatory and collect complete income documents.', 'rental-income':'Compare available rental-income tracks after verifying current thresholds.', 'real-estate-sale':'Check exemption eligibility, family-unit facts, and construction rights before signing.', 'purchase-tax':'Verify current purchase-tax brackets and purchaser status before estimating tax.', 'inheritance-apartment':'Check the deceased person eligibility chain and heir facts before claiming relief.'}
SUMMARY_HE = {
 'vat-registration':'בדוק מעמד במע״מ לפני הוצאת מסמכים או גביית מע״מ.', 'vat-invoice-correction':'תקן מסמכי מע״מ במסלול חוקי התואם למסמך המקורי.', 'foreign-client-vat':'נתח שיעור אפס רק לאחר זיהוי הנהנה בפועל ומקום צריכת השירות.', 'expense-deductibility':'בדוק מטרה עסקית, תיעוד, שימוש פרטי ומגבלות מע״מ בנפרד.', 'withholding-tax':'בדוק תוקף אישור וסוג תשלום לפני קבלת ניכוי מס במקור.', 'annual-return':'קבע אם יש חובת דוח ואסוף מסמכי הכנסה מלאים.', 'rental-income':'השווה מסלולי מס על שכירות לאחר אימות ספים עדכניים.', 'real-estate-sale':'בדוק פטור, תא משפחתי וזכויות בנייה לפני חתימה.', 'purchase-tax':'אמת מדרגות מס רכישה ומעמד רוכש לפני אומדן מס.', 'inheritance-apartment':'בדוק את זכאות המוריש ונתוני היורש לפני דרישת הקלה.'}
POINTS_EN = {
 'vat-registration':['Classify the activity as business, profession, salary, hobby, or capital receipt.','Check whether the profession is excluded from exempt dealer status.','Compare expected turnover with the current official exempt-dealer threshold.','Register before issuing invoices or receipts.','Track turnover during the year and change status when required.'],
 'vat-invoice-correction':['Identify the original document, period, amount, and VAT status.','Determine whether a credit invoice, cancellation, or amended report is required.','Match every correction to the original invoice.','Check interest, linkage, and penalty exposure.'],
 'foreign-client-vat':['Identify the contracting party and actual beneficiary.','Check whether any Israeli resident receives the service or benefit.','Review where the service is used and where deliverables are consumed.','Preserve foreign-residency evidence and contract terms.','Treat zero-rate VAT as conditional until documentation is complete.'],
 'expense-deductibility':['Confirm that the expense was incurred to produce taxable income.','Separate current, capital, private, and mixed-use elements.','Validate invoice, receipt, and payment evidence.','Allocate mixed expenses using a consistent method.','Check VAT input-tax restrictions independently.'],
 'withholding-tax':['Check whether the payer must withhold.','Check current certificate validity and rate.','Match payment type to certificate terms.','Treat withheld tax as a credit against final liability where applicable.'],
 'annual-return':['List all Israeli and foreign income sources.','Check filing exemption versus mandatory filing conditions.','Collect annual tax forms and withholding certificates.','Identify deductions, credits, losses, and advance payments.'],
 'rental-income':['Classify property as residential or commercial.','Identify owner type and monthly rent.','Compare exemption, reduced-rate, and ordinary tracks where available.','Check whether VAT or business classification can arise.'],
 'real-estate-sale':['Identify the real-estate right and asset type.','Check family-unit holdings and prior exemptions.','Verify ownership period, residence, value caps, and construction rights.','Compute gain only after purchase, sale, and improvement data is complete.','Check municipal betterment levy separately.'],
 'purchase-tax':['Identify purchaser status and family-unit holdings.','Classify property and purchase price.','Verify current brackets and reliefs.','Flag replacement-apartment deadlines if another apartment is owned.'],
 'inheritance-apartment':['Confirm legal inheritance status.','Check the deceased person apartment holdings and eligibility.','Check the heir status and sale plan.','Review family-unit and prior-transfer issues.']}
POINTS_HE = {k:[s.replace('Check','בדוק').replace('Identify','זהה').replace('Classify','סווג').replace('Verify','אמת').replace('Review','בדוק').replace('Confirm','אשר') for s in v] for k,v in POINTS_EN.items()}
BASE_WARNINGS_EN=['Verify current thresholds, brackets, forms, and deadlines against official Israel Tax Authority publications.','Do not treat this explanation as a filing, assessment, or legal opinion.']
BASE_WARNINGS_HE=['יש לאמת ספים, מדרגות, טפסים ומועדים מול פרסומי רשות המסים העדכניים.','אין לראות בהסבר דיווח, שומה או חוות דעת משפטית.']
HIGH_RISK={'real-estate-sale','purchase-tax','inheritance-apartment','foreign-client-vat','vat-invoice-correction'}

class TaxLawExplainerClient:
    def __init__(self, *, default_language: str='en') -> None: self.default_language=self._normalize_language(default_language)
    @staticmethod
    def _normalize_language(language: str)->str:
        if language not in {'en','he'}: raise InvalidLanguageError(f'Unsupported language: {language}')
        return language
    @staticmethod
    def topics()->list[str]: return [t.value for t in TaxTopic]
    @staticmethod
    def workflows()->list[str]: return [w.value for w in Workflow]
    @staticmethod
    def missing_facts(topic: str, facts: Mapping[str, Any])->list[str]:
        if topic not in REQUIRED_FACTS: raise UnknownTopicError(f'Unknown topic: {topic}')
        return [name for name in REQUIRED_FACTS[topic] if facts.get(name) in (None,'',[])]
    def explain(self, topic: str, *, user_type: str='unspecified', facts: Mapping[str, Any] | None=None, language: str | None=None)->Explanation:
        lang=self._normalize_language(language or self.default_language)
        if topic not in self.topics(): raise UnknownTopicError(f'Unknown topic: {topic}')
        facts=dict(facts or {}); missing=self.missing_facts(topic, facts)
        warnings=list(BASE_WARNINGS_HE if lang=='he' else BASE_WARNINGS_EN)
        if missing: warnings.append('חסרים נתונים מהותיים; יש לתת תשובה מותנית בלבד.' if lang=='he' else 'Material facts are missing; keep the answer conditional.')
        if topic in HIGH_RISK: warnings.append('נדרש אישור בעל מקצוע לפני דיווח או חתימה.' if lang=='he' else 'Professional review is required before filing or signing.')
        if facts.get('backdating_requested') or facts.get('concealment_requested'): warnings.append('אין לספק הנחיות להסתרה, זיוף או תיארוך לאחור; יש לבחור מסלול תיקון חוקי.' if lang=='he' else 'Do not provide concealment, fabrication, or backdating instructions; use a lawful correction route.')
        docs=list(DOCS[topic]);
        if user_type != 'unspecified': docs.append(f'User type noted: {user_type}')
        return Explanation(topic, lang, (SUMMARY_HE if lang=='he' else SUMMARY_EN)[topic], list((POINTS_HE if lang=='he' else POINTS_EN)[topic]), docs, warnings, bool(topic in HIGH_RISK or missing), missing, list(LEGAL_AREAS[topic]))
    async def aexplain(self, topic: str, *, user_type: str='unspecified', facts: Mapping[str, Any] | None=None, language: str | None=None)->Explanation:
        await asyncio.sleep(0); return self.explain(topic, user_type=user_type, facts=facts, language=language)
    def validate_facts(self, topic: str, facts: Mapping[str, Any] | None=None)->ValidationResult:
        if topic not in self.topics(): raise UnknownTopicError(f'Unknown topic: {topic}')
        facts=dict(facts or {}); missing=self.missing_facts(topic, facts); warnings=[]
        if topic in {'vat-registration','rental-income','purchase-tax','real-estate-sale'}: warnings.append('Verify current thresholds, brackets, and deadlines before producing final numbers.')
        if facts.get('backdating_requested') or facts.get('concealment_requested'): warnings.append('Use only lawful correction or disclosure routes.')
        return ValidationResult(not missing, missing, warnings)
    async def avalidate_facts(self, topic: str, facts: Mapping[str, Any] | None=None)->ValidationResult:
        await asyncio.sleep(0); return self.validate_facts(topic, facts)
    def checklist(self, workflow: str, *, language: str | None=None)->dict[str, Any]:
        lang=self._normalize_language(language or self.default_language)
        if workflow not in self.workflows(): raise UnknownWorkflowError(f'Unknown workflow: {workflow}')
        en={
        'freelancer-onboarding':['Classify activity and expected turnover.','Check VAT status and profession restrictions.','Open required files.','Set bookkeeping method.','Prepare document templates.','Schedule monthly reconciliation.'],
        'vat-documents':['Confirm VAT status.','Confirm transaction and payment timing.','Choose receipt, tax invoice, invoice-receipt, or credit invoice.','Validate required document fields.'],
        'foreign-client-vat':['Identify contracting party.','Identify actual beneficiary.','Check Israeli-resident involvement.','Preserve foreign-use documentation.','Escalate material cases.'],
        'expense-review':['Identify expense type.','Check business purpose.','Validate documentation.','Allocate mixed use.','Check VAT separately.'],
        'withholding-check':['Check certificate validity.','Match payment type.','Compare deducted amount.','Preserve payment statement.'],
        'annual-return':['List income sources.','Collect annual forms.','Check mandatory filing rules.','Summarize deductions and credits.'],
        'rental-income':['Classify property.','Calculate monthly rent.','Compare available tracks.','Check VAT and National Insurance exposure.'],
        'real-estate-sale':['Collect acquisition and sale documents.','Check exemption eligibility.','Check construction rights.','Check municipal betterment levy.','Prepare reporting calendar.'],
        'purchase-tax':['Identify purchaser status.','Classify asset.','Verify current brackets.','Check replacement-apartment deadlines.'],
        'tax-authority-letter':['Identify issuing unit.','Extract deadline and requested action.','Prepare document index.','Escalate assessments and audits.']}
        he={k:[x.replace('VAT','מע״מ').replace('Check','בדוק').replace('Identify','זהה').replace('Classify','סווג').replace('Collect','אסוף').replace('Prepare','הכן').replace('Verify','אמת') for x in v] for k,v in en.items()}
        return {'workflow':workflow,'language':lang,'steps':(he if lang=='he' else en)[workflow]}
    async def achecklist(self, workflow: str, *, language: str | None=None)->dict[str, Any]: await asyncio.sleep(0); return self.checklist(workflow, language=language)
    @staticmethod
    def reference_values() -> dict[str, object]:
        """Return web-validated reference values captured for this package release."""
        return dict(CURRENT_REFERENCE_VALUES)

    def export_scenario(self, name: str, output: str | Path, *, language: str='en')->Path:
        path=Path(output); path.write_text(json.dumps(scenario_payload(name, language=language), ensure_ascii=False, indent=2), encoding='utf-8'); return path

def scenario_payload(name: str, *, language: str='en')->dict[str, Any]:
    if language not in {'en','he'}: raise InvalidLanguageError(f'Unsupported language: {language}')
    scenarios={
    'freelancer_home_office': {'topic':'expense-deductibility','facts':{'expense_type':'home internet','business_purpose':'client work from home office','has_invoice':True,'business_use_percent':60}},
    'foreign_client': {'topic':'foreign-client-vat','facts':{'client_residence':'United States','beneficiary':'foreign company','use_location':'outside Israel','contract':'signed service agreement'}},
    'apartment_sale': {'topic':'real-estate-sale','facts':{'asset_type':'residential_apartment','purchase_date':'15-06-2018','sale_date':'20-07-2026','purchase_price':1600000,'sale_price':2400000,'family_unit_holdings':'one apartment','construction_rights':False}},
    'withholding': {'topic':'withholding-tax','facts':{'payer':'customer','payee':'freelancer','payment_type':'services','certificate_valid':True}},
    'rental_income': {'topic':'rental-income','facts':{'property_type':'residential','monthly_rent':5200,'owner_type':'individual'}}}
    if name not in scenarios: raise KeyError(f'Unknown scenario: {name}')
    out=dict(scenarios[name]); out['language']=language; return out

def load_facts_json(value: str | Path | None)->dict[str, Any]:
    if value is None or value=='': return {}
    s=str(value); text=Path(s).read_text(encoding='utf-8') if Path(s).exists() else s
    loaded=json.loads(text)
    if not isinstance(loaded, dict): raise TypeError('Facts JSON must decode to an object')
    return loaded

CURRENT_REFERENCE_VALUES: dict[str, object] = {
    "access_date": "2026-06-02",
    "standard_vat_rate_percent": 18,
    "vat_rate_effective_from": "2025-01-01",
    "exempt_dealer_threshold_2026_nis": 122833,
    "residential_rent_exemption_ceiling_monthly_nis": 5654,
    "rental_income_section_122_rate_percent": 10,
    "annual_return_2025_non_online_deadline": "2026-05-29",
    "annual_return_2025_online_deadline": "2026-06-30",
    "real_estate_declaration_deadline_days": 30,
    "official_api_docs_require_registration": True,
}
