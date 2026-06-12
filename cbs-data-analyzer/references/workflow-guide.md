# Workflow Guide

## Workflow 1: CPI-linked rent adjustment

Use when a tenant, landlord, freelancer, or business asks for an indexed amount.

### Inputs

- original amount, such as `₪5,200`;
- base CPI value and base period;
- target CPI value and target period;
- contract clause, cap/floor, and rounding rule if available.

### Steps

1. Confirm that the clause refers to the Consumer Price Index and not another index.
2. Fetch or verify CPI series code `120010` from the CBS catalog.
3. Use index levels, not percentage changes.
4. Calculate `amount × target_index / base_index`.
5. Apply cap, floor, rounding, and timing rules only if supplied.
6. State reference periods and limitations.

### Output

```text
Original amount: ₪5,200
Base period: 01-01-2025, CPI 103.1
Target period: 01-04-2026, CPI 106.4
Formula: 5,200 × 106.4 / 103.1
Adjusted amount: ₪5,366.44
Change: 3.20%
```

### Decision caveat

Apply only under the signed agreement and current law. The calculation does not determine enforceability.

## Workflow 2: Price increase for a small service business

Use when a barber, cleaner, designer, technician, tutor, or consultant asks whether to raise prices.

### Inputs

- current price and last update date;
- cost drivers: labour, rent, materials, fuel, insurance, platform fees;
- relevant CPI or input-cost index;
- customer segment and churn sensitivity.

### Steps

1. Fetch CPI for broad purchasing-power erosion.
2. Search catalog for a more relevant input index if costs are sector-specific.
3. Calculate inflation-maintenance price.
4. Compare with margin erosion and competitor constraints.
5. Present options: no change, CPI-only update, cost-based update, or phased update.
6. Include sample customer communication when requested.

### Output structure

| Option | Price | Rationale | Risk |
|---|---:|---|---|
| Maintain | ₪250 | Avoid churn | Margin erosion continues |
| CPI-linked | ₪262 | Preserves purchasing power | Moderate customer reaction |
| Cost-based | ₪275 | Covers rent and wage pressure | Higher churn risk |
| Phased | ₪260 now, ₪270 later | Reduces shock | Requires notice and tracking |

## Workflow 3: Local demand screen for a retail location

Use for cafés, clinics, studios, convenience stores, tutoring centers, pet services, and similar local businesses.

### Inputs

- locality or neighbourhood;
- target customer;
- radius or catchment area;
- service category;
- desired opening date.

### Steps

1. Search CBS locality or population datasets through data.gov.il organization `lamas`.
2. Extract population, households, age groups, and density if available.
3. Add labour or commuting context if relevant.
4. Add price index context for costs.
5. Keep competition analysis separate because CBS does not fully measure it.
6. Produce a scorecard with evidence and missing data.

### Scorecard template

| Signal | Data | Interpretation | Confidence |
|---|---|---|---|
| Resident base | Population and households | Local baseline demand | Medium |
| Age fit | Age-group share | Product fit | Medium |
| Daytime demand | Employment/commuting proxy | Lunch/weekday demand | Low to medium |
| Cost pressure | CPI/input index | Pricing pressure | Medium |
| Competition | External map/field data | Must be checked separately | Low until verified |

## Workflow 4: Supplier contract indexation

Use when a supplier asks for an increase and cites inflation.

### Inputs

- current contract price;
- previous update date;
- supplier's claimed increase;
- named index in the agreement;
- supplier cost categories.

### Steps

1. Read the indexation clause.
2. Use the exact index if named; search catalog by Hebrew and English terms.
3. If no index is named, show CPI and explain its limits.
4. Calculate the CPI-linked and input-index-linked benchmarks separately.
5. Recommend a future clause with index name, code, review frequency, cap, floor, and rounding.

### Clause design checklist

- exact CBS series name and code;
- base date and target date;
- update frequency;
- cap and floor;
- rounding rule;
- notice period;
- treatment of discontinued series;
- treatment of VAT.

## Workflow 5: Housing trend check for consumers

Use when a buyer, renter, seller, or real-estate-adjacent business asks about market direction.

### Inputs

- district, locality, or national level;
- apartment type if available;
- decision: buy, sell, rent, open business, or negotiate.

### Steps

1. Search the CBS index catalog for the relevant housing index.
2. Fetch latest values and recent history.
3. Compare monthly, quarterly, and annual changes.
4. Flag that the series reflects transaction mix and reporting lag.
5. Avoid a valuation of a specific property.
6. Recommend complementary evidence: comparable transactions, appraisal, mortgage terms, and property condition.

## Workflow 6: Freelancer rate benchmark

Use for retainers, hourly rates, and annual price updates.

### Inputs

- current rate;
- last update month;
- service scope;
- VAT status;
- target customer segment.

### Steps

1. Compute CPI-linked equivalent.
2. Check whether scope expanded.
3. Use wage or labour data only as context if relevant and current.
4. Present a range and negotiation framing.
5. Keep VAT, income tax, and national insurance separate from price benchmarking.

## Workflow 7: Consumer budget impact

Use when a household asks how inflation affects a budget.

### Inputs

- monthly budget by categories;
- reference period;
- CPI component changes if available.

### Steps

1. Fetch CPI headline and relevant component indices if available.
2. Match user categories to CBS components cautiously.
3. Explain that personal inflation may differ from headline CPI.
4. Calculate an illustrative effect.
5. Avoid claims about entitlement or compensation.

## Workflow 8: Construction or renovation escalation

Use when a contractor, homeowner, or property manager has a building-input clause.

### Inputs

- contract sum;
- base index;
- target index;
- index series named in contract;
- milestones and payment schedule.

### Steps

1. Search for the exact building-input index in the CBS catalog.
2. Calculate indexation per milestone, not only for the total, when payment dates matter.
3. Keep VAT and retentions separate.
4. Show both unrounded and rounded amounts.
5. Add a discontinued-series fallback clause if drafting guidance is requested.
