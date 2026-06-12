"""Israeli import-tax estimation models and client helpers.

The module performs deterministic calculations from supplied or verified rates.
It does not replace official tariff lookup, binding classification, or customs
broker review.
"""

from __future__ import annotations

import asyncio
import json
import re
import uuid
from dataclasses import asdict, dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence


MONEY_QUANT = Decimal("0.01")


class TariffAdvisorError(ValueError):
    """Base validation error for tariff estimates."""


class RateValidationError(TariffAdvisorError):
    """Raised when a tax rate is outside the accepted decimal range."""


class MoneyValidationError(TariffAdvisorError):
    """Raised when a monetary input is invalid."""


def _decimal(value: Any, field_name: str) -> Decimal:
    """Convert user input to Decimal while producing friendly errors."""
    try:
        dec = Decimal(str(value))
    except Exception as exc:
        raise MoneyValidationError(f"{field_name} must be numeric") from exc
    if not dec.is_finite():
        raise MoneyValidationError(f"{field_name} must be finite")
    return dec


def _money(value: Any, field_name: str) -> Decimal:
    dec = _decimal(value, field_name)
    if dec < 0:
        raise MoneyValidationError(f"{field_name} must be non-negative")
    return dec


def _positive(value: Any, field_name: str) -> Decimal:
    dec = _decimal(value, field_name)
    if dec <= 0:
        raise MoneyValidationError(f"{field_name} must be positive")
    return dec


def _rate(value: Any, field_name: str) -> Decimal:
    dec = _decimal(value, field_name)
    if dec < 0 or dec > 1:
        raise RateValidationError(f"{field_name} rate must be between 0 and 1")
    return dec


def _round_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def normalize_tariff_code(code: Optional[str]) -> Optional[str]:
    """Normalize a tariff code by removing separators."""
    if code is None:
        return None
    normalized = re.sub(r"[^0-9]", "", code)
    return normalized or None


REGULATED_KEYWORDS = {
    "wireless": ["wifi", "wi-fi", "bluetooth", "cellular", "radio", "router", "transmitter"],
    "food": ["food", "supplement", "vitamin", "coffee", "tea", "snack", "wine", "beer"],
    "cosmetics": ["cosmetic", "cream", "lotion", "perfume", "makeup"],
    "medical": ["medical", "diagnostic", "blood pressure", "syringe", "device"],
    "vehicle": ["vehicle", "car", "brake", "tire", "tyre", "motorcycle", "engine"],
}


@dataclass(frozen=True)
class LineItem:
    """One import line item."""

    description: str
    goods_value: Decimal
    shipping: Decimal = Decimal("0")
    insurance: Decimal = Decimal("0")
    exchange_rate_to_ils: Decimal = Decimal("1")
    duty_rate: Decimal = Decimal("0")
    purchase_tax_rate: Decimal = Decimal("0")
    vat_rate: Decimal = Decimal("0.18")
    taxable_fees_ils: Decimal = Decimal("0")
    non_tax_fees_ils: Decimal = Decimal("0")
    quantity: Decimal = Decimal("1")
    tariff_code: Optional[str] = None
    origin_country: Optional[str] = None
    importer_type: Optional[str] = None
    use_type: Optional[str] = None
    estimate_date: Optional[str] = None
    environment: str = "sandbox"

    @classmethod
    def create(
        cls,
        *,
        description: str,
        goods_value: Any,
        shipping: Any = 0,
        insurance: Any = 0,
        exchange_rate_to_ils: Any = 1,
        duty_rate: Any = 0,
        purchase_tax_rate: Any = 0,
        vat_rate: Any = 0.18,
        taxable_fees_ils: Any = 0,
        non_tax_fees_ils: Any = 0,
        quantity: Any = 1,
        tariff_code: Optional[str] = None,
        origin_country: Optional[str] = None,
        importer_type: Optional[str] = None,
        use_type: Optional[str] = None,
        estimate_date: Optional[str] = None,
        environment: str = "sandbox",
    ) -> "LineItem":
        desc = (description or "").strip()
        if len(desc) < 3:
            raise TariffAdvisorError("description must contain at least 3 characters")
        env = (environment or "sandbox").strip().lower()
        if env not in {"sandbox", "production"}:
            raise TariffAdvisorError("environment must be sandbox or production")
        return cls(
            description=desc,
            goods_value=_money(goods_value, "goods_value"),
            shipping=_money(shipping, "shipping"),
            insurance=_money(insurance, "insurance"),
            exchange_rate_to_ils=_positive(exchange_rate_to_ils, "exchange_rate_to_ils"),
            duty_rate=_rate(duty_rate, "duty_rate"),
            purchase_tax_rate=_rate(purchase_tax_rate, "purchase_tax_rate"),
            vat_rate=_rate(vat_rate, "vat_rate"),
            taxable_fees_ils=_money(taxable_fees_ils, "taxable_fees_ils"),
            non_tax_fees_ils=_money(non_tax_fees_ils, "non_tax_fees_ils"),
            quantity=_positive(quantity, "quantity"),
            tariff_code=normalize_tariff_code(tariff_code),
            origin_country=origin_country,
            importer_type=importer_type,
            use_type=use_type,
            estimate_date=estimate_date,
            environment=env,
        )


@dataclass(frozen=True)
class EstimateResult:
    """Calculated estimate for one or more import line items."""

    currency: str
    customs_value: Decimal
    customs_duty: Decimal
    purchase_tax: Decimal
    vat_base: Decimal
    vat: Decimal
    total_taxes: Decimal
    non_tax_fees: Decimal
    landed_cost: Decimal
    line_count: int
    estimate_id: Optional[str] = None
    environment: str = "sandbox"
    assumptions: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    line_results: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-friendly dictionary."""
        def convert(value: Any) -> Any:
            if isinstance(value, Decimal):
                return float(value)
            if isinstance(value, list):
                return [convert(v) for v in value]
            if isinstance(value, dict):
                return {k: convert(v) for k, v in value.items()}
            return value

        return convert(asdict(self))

    def to_json(self, *, ensure_ascii: bool = False, indent: Optional[int] = 2) -> str:
        """Serialize the estimate as JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=ensure_ascii, indent=indent)


class TariffAdvisorClient:
    """Synchronous and asynchronous import-tax estimate client."""

    def __init__(self, *, default_vat_rate: Any = 0.18, store_path: Optional[str | Path] = None) -> None:
        self.default_vat_rate = _rate(default_vat_rate, "default_vat_rate")
        self.store_path = Path(store_path) if store_path else None

    def estimate(
        self,
        *,
        description: str,
        goods_value: Any,
        shipping: Any = 0,
        insurance: Any = 0,
        exchange_rate_to_ils: Any = 1,
        duty_rate: Any = 0,
        purchase_tax_rate: Any = 0,
        vat_rate: Optional[Any] = None,
        taxable_fees_ils: Any = 0,
        non_tax_fees_ils: Any = 0,
        quantity: Any = 1,
        tariff_code: Optional[str] = None,
        origin_country: Optional[str] = None,
        importer_type: Optional[str] = None,
        use_type: Optional[str] = None,
        estimate_date: Optional[str] = None,
        environment: str = "sandbox",
    ) -> EstimateResult:
        """Estimate one import line item."""
        item = LineItem.create(
            description=description,
            goods_value=goods_value,
            shipping=shipping,
            insurance=insurance,
            exchange_rate_to_ils=exchange_rate_to_ils,
            duty_rate=duty_rate,
            purchase_tax_rate=purchase_tax_rate,
            vat_rate=self.default_vat_rate if vat_rate is None else vat_rate,
            taxable_fees_ils=taxable_fees_ils,
            non_tax_fees_ils=non_tax_fees_ils,
            quantity=quantity,
            tariff_code=tariff_code,
            origin_country=origin_country,
            importer_type=importer_type,
            use_type=use_type,
            estimate_date=estimate_date,
            environment=environment,
        )
        return self.estimate_lines([item])

    async def estimate_async(self, **kwargs: Any) -> EstimateResult:
        """Asynchronously estimate one import line item."""
        await asyncio.sleep(0)
        return self.estimate(**kwargs)

    def estimate_lines(self, items: Sequence[LineItem]) -> EstimateResult:
        """Estimate a shipment made of one or more line items."""
        if not items:
            raise TariffAdvisorError("at least one line item is required")

        line_results: List[Dict[str, Any]] = []
        warnings: List[str] = []
        assumptions: List[str] = [
            "Rates are supplied or configured; verify official tariff, VAT, and exchange-rate sources before filing",
            "Customs value uses goods + international shipping + insurance",
        ]
        environment = items[0].environment

        totals = {
            "customs_value": Decimal("0"),
            "customs_duty": Decimal("0"),
            "purchase_tax": Decimal("0"),
            "vat_base": Decimal("0"),
            "vat": Decimal("0"),
            "non_tax_fees": Decimal("0"),
            "landed_cost": Decimal("0"),
        }

        for item in items:
            line = self._estimate_line(item)
            line_results.append(line)
            for key in totals:
                totals[key] += Decimal(str(line[key]))
            warnings.extend(self._warnings_for_item(item))
            if item.environment != environment:
                warnings.append("Mixed environments supplied; use one environment per estimate batch")

        if len(items) > 1:
            warnings.append("Mixed shipment: verify each line item has its own Israeli tariff classification")
            assumptions.append("Shipping allocation is assumed to be already included per line item")

        return EstimateResult(
            currency="ILS",
            customs_value=_round_money(totals["customs_value"]),
            customs_duty=_round_money(totals["customs_duty"]),
            purchase_tax=_round_money(totals["purchase_tax"]),
            vat_base=_round_money(totals["vat_base"]),
            vat=_round_money(totals["vat"]),
            total_taxes=_round_money(totals["customs_duty"] + totals["purchase_tax"] + totals["vat"]),
            non_tax_fees=_round_money(totals["non_tax_fees"]),
            landed_cost=_round_money(totals["landed_cost"]),
            line_count=len(items),
            environment=environment,
            assumptions=assumptions,
            warnings=sorted(set(warnings)),
            line_results=line_results,
        )

    async def estimate_lines_async(self, items: Sequence[LineItem]) -> EstimateResult:
        """Asynchronously estimate a multi-line shipment."""
        await asyncio.sleep(0)
        return self.estimate_lines(items)

    def create_estimate(self, **kwargs: Any) -> EstimateResult:
        """Create an estimate, assign an identifier, and save it when a store path is configured."""
        result = self.estimate(**kwargs)
        result_with_id = EstimateResult(
            currency=result.currency,
            customs_value=result.customs_value,
            customs_duty=result.customs_duty,
            purchase_tax=result.purchase_tax,
            vat_base=result.vat_base,
            vat=result.vat,
            total_taxes=result.total_taxes,
            non_tax_fees=result.non_tax_fees,
            landed_cost=result.landed_cost,
            line_count=result.line_count,
            estimate_id=f"est_{uuid.uuid4().hex[:12]}",
            environment=result.environment,
            assumptions=result.assumptions,
            warnings=result.warnings,
            line_results=result.line_results,
        )
        self._save_result(result_with_id)
        return result_with_id

    async def create_estimate_async(self, **kwargs: Any) -> EstimateResult:
        """Asynchronously create and save an estimate."""
        await asyncio.sleep(0)
        return self.create_estimate(**kwargs)

    def get_estimate(self, estimate_id: str) -> EstimateResult:
        """Load a stored estimate by identifier."""
        if not self.store_path:
            raise TariffAdvisorError("store_path is required to retrieve estimates")
        store = self._load_store()
        if estimate_id not in store:
            raise TariffAdvisorError(f"estimate_id not found: {estimate_id}")
        return self._result_from_dict(store[estimate_id])

    async def get_estimate_async(self, estimate_id: str) -> EstimateResult:
        """Asynchronously load a stored estimate by identifier."""
        await asyncio.sleep(0)
        return self.get_estimate(estimate_id)

    def estimate_from_mapping(self, data: Mapping[str, Any]) -> EstimateResult:
        """Estimate from a mapping."""
        return self.estimate(**dict(data))

    def estimate_from_json_file(self, path: str | Path) -> EstimateResult:
        """Estimate from a JSON file containing one estimate object or line_items."""
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(payload, dict) and "line_items" in payload:
            return self.estimate_lines([LineItem.create(**item) for item in payload["line_items"]])
        if isinstance(payload, dict):
            return self.estimate_from_mapping(payload)
        raise TariffAdvisorError("JSON input must be an object")

    def _estimate_line(self, item: LineItem) -> Dict[str, Any]:
        customs_value = (item.goods_value + item.shipping + item.insurance) * item.exchange_rate_to_ils
        customs_duty = customs_value * item.duty_rate
        purchase_tax_base = customs_value + customs_duty
        purchase_tax = purchase_tax_base * item.purchase_tax_rate
        vat_base = customs_value + customs_duty + purchase_tax + item.taxable_fees_ils
        vat = vat_base * item.vat_rate
        total_taxes = customs_duty + purchase_tax + vat
        landed_cost = customs_value + total_taxes + item.non_tax_fees_ils

        return {
            "description": item.description,
            "tariff_code": item.tariff_code,
            "customs_value": _round_money(customs_value),
            "customs_duty": _round_money(customs_duty),
            "purchase_tax": _round_money(purchase_tax),
            "vat_base": _round_money(vat_base),
            "vat": _round_money(vat),
            "total_taxes": _round_money(total_taxes),
            "non_tax_fees": _round_money(item.non_tax_fees_ils),
            "landed_cost": _round_money(landed_cost),
        }

    def _warnings_for_item(self, item: LineItem) -> List[str]:
        warnings: List[str] = []
        text = item.description.lower()

        if item.shipping == 0:
            warnings.append("Shipping is zero; confirm freight is genuinely included or free")
        if item.tariff_code is None:
            warnings.append("No Israeli tariff code supplied; classification must be verified")
        if item.purchase_tax_rate > 0:
            warnings.append("Purchase tax applied; verify calculation base and tariff-specific rules")
        if item.quantity >= 20 and (item.use_type or "").lower() != "personal":
            warnings.append("Commercial quantity: verify import approvals and business documentation")
        if any(word in text for word in REGULATED_KEYWORDS["wireless"]):
            warnings.append("Wireless/communications product: check Ministry of Communications approval or exemption")
        if any(word in text for word in REGULATED_KEYWORDS["food"]):
            warnings.append("Food, supplement, or alcohol signal: check health/agriculture/alcohol import rules")
        if any(word in text for word in REGULATED_KEYWORDS["cosmetics"]):
            warnings.append("Cosmetics signal: check Ministry of Health requirements")
        if any(word in text for word in REGULATED_KEYWORDS["medical"]):
            warnings.append("Medical device signal: check Ministry of Health registration requirements")
        if any(word in text for word in REGULATED_KEYWORDS["vehicle"]):
            warnings.append("Vehicle or vehicle-part signal: check Ministry of Transport and purchase tax treatment")
        if item.origin_country:
            warnings.append("Origin supplied; verify proof of origin before applying preferential duty")
        if item.environment == "production":
            warnings.append("Production environment selected; verify live official rates before operational use")
        if (item.use_type or "").lower() == "personal":
            warnings.append("Personal-import relief thresholds can change; verify the current threshold on the estimate date")
        return warnings

    def _load_store(self) -> Dict[str, Any]:
        if not self.store_path:
            return {}
        if not self.store_path.exists():
            return {}
        return json.loads(self.store_path.read_text(encoding="utf-8"))

    def _save_result(self, result: EstimateResult) -> None:
        if not self.store_path or not result.estimate_id:
            return
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        store = self._load_store()
        store[result.estimate_id] = result.to_dict()
        self.store_path.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")

    def _result_from_dict(self, data: Mapping[str, Any]) -> EstimateResult:
        return EstimateResult(
            currency=str(data["currency"]),
            customs_value=_round_money(_decimal(data["customs_value"], "customs_value")),
            customs_duty=_round_money(_decimal(data["customs_duty"], "customs_duty")),
            purchase_tax=_round_money(_decimal(data["purchase_tax"], "purchase_tax")),
            vat_base=_round_money(_decimal(data["vat_base"], "vat_base")),
            vat=_round_money(_decimal(data["vat"], "vat")),
            total_taxes=_round_money(_decimal(data["total_taxes"], "total_taxes")),
            non_tax_fees=_round_money(_decimal(data["non_tax_fees"], "non_tax_fees")),
            landed_cost=_round_money(_decimal(data["landed_cost"], "landed_cost")),
            line_count=int(data["line_count"]),
            estimate_id=data.get("estimate_id"),
            environment=str(data.get("environment", "sandbox")),
            assumptions=list(data.get("assumptions", [])),
            warnings=list(data.get("warnings", [])),
            line_results=list(data.get("line_results", [])),
        )


__all__ = [
    "EstimateResult",
    "LineItem",
    "MoneyValidationError",
    "RateValidationError",
    "TariffAdvisorClient",
    "TariffAdvisorError",
    "normalize_tariff_code",
]
