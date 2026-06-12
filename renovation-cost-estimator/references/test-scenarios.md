# Test Scenarios

## Scenario 1: Standard apartment

```json
{
  "city": "Ramat Gan",
  "property_type": "apartment",
  "area_sqm": 72,
  "scope_level": "partial",
  "finish_level": "standard",
  "bathrooms": 1,
  "kitchens": 1,
  "include_vat": true
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 2: Cosmetic rental refresh

```json
{
  "city": "Haifa",
  "property_type": "apartment",
  "area_sqm": 55,
  "scope_level": "cosmetic",
  "finish_level": "basic",
  "include_vat": true
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 3: Premium full apartment

```json
{
  "city": "Tel Aviv",
  "property_type": "apartment",
  "area_sqm": 95,
  "scope_level": "full",
  "finish_level": "premium",
  "bathrooms": 2,
  "kitchens": 1,
  "include_vat": true
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 4: Old no elevator

```json
{
  "city": "Holon",
  "property_type": "apartment",
  "area_sqm": 82,
  "scope_level": "partial",
  "finish_level": "standard",
  "building_year": 1975,
  "floor": 4,
  "has_elevator": false,
  "include_vat": true
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 5: Occupied apartment

```json
{
  "city": "Petah Tikva",
  "property_type": "apartment",
  "area_sqm": 70,
  "scope_level": "partial",
  "finish_level": "standard",
  "occupied": true,
  "include_vat": true
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 6: Clinic fit-out

```json
{
  "city": "Tel Aviv",
  "property_type": "clinic",
  "area_sqm": 38,
  "scope_level": "commercial_fitout",
  "finish_level": "standard",
  "rooms": 3,
  "wet_rooms": 1,
  "requires_business_license": true,
  "commercial_public_access": true,
  "include_vat": false
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 7: Retail shop

```json
{
  "city": "Jerusalem",
  "property_type": "shop",
  "area_sqm": 42,
  "scope_level": "retail_fitout",
  "finish_level": "premium",
  "requires_business_license": true,
  "signage": true,
  "include_vat": false
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 8: Small office

```json
{
  "city": "Bnei Brak",
  "property_type": "office",
  "area_sqm": 60,
  "scope_level": "office_fitout",
  "finish_level": "standard",
  "include_vat": false
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 9: Shell apartment

```json
{
  "city": "Netanya",
  "property_type": "apartment",
  "area_sqm": 95,
  "scope_level": "shell",
  "finish_level": "standard",
  "bathrooms": 2,
  "kitchens": 1,
  "include_vat": true
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 10: Bathroom only

```json
{
  "city": "Rehovot",
  "property_type": "apartment",
  "area_sqm": 8,
  "scope_level": "partial",
  "finish_level": "standard",
  "line_items": [
    {
      "category": "bathroom_full",
      "quantity": 1
    }
  ],
  "include_vat": true
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 11: Kitchen only

```json
{
  "city": "Givatayim",
  "property_type": "apartment",
  "area_sqm": 12,
  "scope_level": "partial",
  "finish_level": "premium",
  "line_items": [
    {
      "category": "kitchen_full",
      "quantity": 1
    }
  ],
  "include_vat": true
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 12: Measured trades

```json
{
  "city": "Rishon LeZion",
  "property_type": "apartment",
  "area_sqm": 80,
  "scope_level": "partial",
  "finish_level": "standard",
  "line_items": [
    {
      "category": "floor_tiling",
      "quantity": 80
    },
    {
      "category": "electrical_point",
      "quantity": 45
    },
    {
      "category": "paint",
      "quantity": 220
    }
  ],
  "include_vat": true
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 13: Invalid area

```json
{
  "city": "Haifa",
  "property_type": "apartment",
  "area_sqm": 0,
  "scope_level": "partial",
  "finish_level": "standard"
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 14: Unknown finish

```json
{
  "city": "Haifa",
  "property_type": "apartment",
  "area_sqm": 60,
  "scope_level": "partial",
  "finish_level": "gold"
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 15: Unknown line

```json
{
  "city": "Haifa",
  "property_type": "apartment",
  "area_sqm": 60,
  "scope_level": "partial",
  "finish_level": "standard",
  "line_items": [
    {
      "category": "marble_dragon",
      "quantity": 1
    }
  ]
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 16: Negative quantity

```json
{
  "city": "Haifa",
  "property_type": "apartment",
  "area_sqm": 60,
  "scope_level": "partial",
  "finish_level": "standard",
  "line_items": [
    {
      "category": "paint",
      "quantity": -4
    }
  ]
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 17: VAT excluded office

```json
{
  "city": "Tel Aviv",
  "property_type": "office",
  "area_sqm": 45,
  "scope_level": "office_fitout",
  "finish_level": "standard",
  "include_vat": false
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 18: Custom VAT

```json
{
  "city": "Tel Aviv",
  "property_type": "office",
  "area_sqm": 45,
  "scope_level": "office_fitout",
  "finish_level": "standard",
  "vat_rate": 0.17,
  "include_vat": true
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 19: Structural old building

```json
{
  "city": "Jerusalem",
  "property_type": "apartment",
  "area_sqm": 90,
  "scope_level": "full",
  "finish_level": "standard",
  "building_year": 1965,
  "structural_changes": true,
  "include_vat": true
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 20: Food shop

```json
{
  "city": "Ashdod",
  "property_type": "shop",
  "area_sqm": 50,
  "scope_level": "retail_fitout",
  "finish_level": "standard",
  "food_business": true,
  "requires_business_license": true,
  "include_vat": false
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 21: Dense Tel Aviv no elevator

```json
{
  "city": "Tel Aviv",
  "property_type": "apartment",
  "area_sqm": 65,
  "scope_level": "partial",
  "finish_level": "standard",
  "floor": 5,
  "has_elevator": false,
  "include_vat": true
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 22: Quote sanity

```json
{
  "city": "Ramat Gan",
  "property_type": "apartment",
  "area_sqm": 80,
  "scope_level": "full",
  "finish_level": "standard",
  "contractor_quote_total": 300000,
  "contractor_quote_includes_vat": false,
  "include_vat": true
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 23: Hebrew output

```json
{
  "project_name": "שיפוץ קליניקה",
  "city": "תל אביב",
  "property_type": "clinic",
  "area_sqm": 38,
  "scope_level": "commercial_fitout",
  "finish_level": "standard",
  "include_vat": false,
  "language": "he"
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.

## Scenario 24: High risk commercial

```json
{
  "city": "Tel Aviv",
  "property_type": "clinic",
  "area_sqm": 80,
  "scope_level": "commercial_fitout",
  "finish_level": "premium",
  "building_year": 1960,
  "occupied": true,
  "requires_business_license": true,
  "commercial_public_access": true,
  "structural_changes": true
}
```

Expected: validate totals, VAT behavior, risks, and assumptions for this case.


## Official-source note

Use official sources for VAT, price-index movement, permits, business licensing, accessibility, fire safety, health, waste, asbestos, and standards. Use per-meter and per-room amounts only as planning heuristics until written contractor quotes are received.
