# Green Invoice API Reference

This reference summarizes the Green Invoice (Morning) API surface used by the bundled client, CLI, examples, and tests. It is intentionally neutral and implementation-focused.

## Base URLs

| Environment | URL |
|---|---|
| Production | `https://api.greeninvoice.co.il/api/v1` |
| sandbox | `https://sandbox.d.greeninvoice.co.il/api/v1` |
| WebSocket | `wss://wss.greeninvoice.co.il` |

## Authentication

Authenticate with `POST /account/token`, including `id`, `secret`, and `grant_type: "client_credentials"`, then use `Authorization: Bearer <accessToken>`. Tokens are short-lived; refresh before expiry or once after a 401 response.

## Endpoint catalogue

### POST /account/token — Authenticate

Exchange API key id and secret, plus `grant_type: "client_credentials"`, for a bearer access token.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| `id` | yes | str | Validate according to endpoint semantics and account permissions. |
| `secret` | yes | str | Validate according to endpoint semantics and account permissions. |

**Request example**

```json
{
  "id": "api_key_id",
  "secret": "api_key_secret",
  "grant_type": "client_credentials"
}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `accessToken` | str | Current bearer token field in the developer docs. |
| `token` | str | Backward-compatible field accepted by the bundled client where returned. |
| `expiresIn` | int | Token lifetime in seconds where returned. |
| `tokenType` | str | Usually `Bearer` where returned. |
| `expires` | int | Returned by the endpoint. |

**Response example**

```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.sample.signature",
  "tokenType": "Bearer",
  "expiresIn": 3600
}
```

### GET /users/me — Verify user

Return the authenticated user profile and active business context.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| path/header parameters | yes | string | Use path `{id}` when present and `Authorization` for authenticated endpoints. |

**Request example**

```json
{}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Returned by the endpoint. |
| `name` | str | Returned by the endpoint. |
| `email` | str | Returned by the endpoint. |
| `businessId` | str | Returned by the endpoint. |
| `roles` | array | Returned by the endpoint. |

**Response example**

```json
{
  "id": "usr_8f42",
  "name": "Dana Cohen",
  "email": "dana@example.co.il",
  "businessId": "biz_9a10",
  "roles": [
    "admin"
  ]
}
```

### GET /businesses — List businesses

List businesses available to the authenticated user.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| path/header parameters | yes | string | Use path `{id}` when present and `Authorization` for authenticated endpoints. |

**Request example**

```json
{}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `items` | array | Returned by the endpoint. |

**Response example**

```json
{
  "items": [
    {
      "id": "biz_9a10",
      "name": "Dana Cohen Consulting",
      "type": 1,
      "taxId": "012345678",
      "country": "IL",
      "currency": "ILS",
      "vatRate": 0.18
    }
  ]
}
```

### POST /businesses/search — Search businesses

Search accessible businesses.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| `name` | yes | str | Validate according to endpoint semantics and account permissions. |
| `page` | optional | int | Validate according to endpoint semantics and account permissions. |
| `pageSize` | optional | int | Validate according to endpoint semantics and account permissions. |

**Request example**

```json
{
  "name": "Dana",
  "page": 0,
  "pageSize": 20
}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `items` | array | Returned by the endpoint. |
| `page` | int | Returned by the endpoint. |
| `pageSize` | int | Returned by the endpoint. |
| `total` | int | Returned by the endpoint. |

**Response example**

```json
{
  "items": [
    {
      "id": "biz_9a10",
      "name": "Dana Cohen Consulting",
      "type": 1,
      "taxId": "012345678"
    }
  ],
  "page": 0,
  "pageSize": 20,
  "total": 1
}
```

### POST /documents — Create document

Create and issue a document.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| `type` | yes | integer | One of 10,100,200,210,300,305,320,330,400,405,500,600,610. |
| `date` | yes | date | `YYYY-MM-DD`; use Israel business date for issued documents. |
| `dueDate` | optional | date | Required when payment due date is relevant. |
| `lang` | optional | string | `he` or `en`. |
| `currency` | optional | string | ISO-like currency enum such as ILS, USD, EUR. |
| `vatType` | optional | integer | 0 default, 1 exempt, 2 mixed. |
| `client` | yes | object | Either existing `id` or complete client fields. |
| `income` | conditional | array | Required for revenue and tax documents; line `description`, `quantity`, `price`. |
| `payment` | conditional | array | Required for receipt documents and type 320 when payment is recorded. |
| `discount` | optional | object | `amount` plus `type`=`sum` or `percentage`. |
| `rounding` | optional | boolean | Round fractional agorot at document level. |
| `signed` | optional | boolean | Create signed file where account supports it. |
| `attachment` | optional | boolean | Generate attachment/download links. |
| `linkedDocumentIds` | optional | array[string] | Use for closing, crediting, or lifecycle relationships. |
| `linkType` | optional | string | `link` or `cancel`. |

**Request example**

```json
{
  "description": "May 2026 implementation services",
  "remarks": "Payment received by bank transfer on 2026-05-31.",
  "footer": "Thank you for your business.",
  "emailContent": "Hello, attached is the tax invoice-receipt for May 2026 services.",
  "type": 320,
  "date": "2026-05-31",
  "dueDate": "2026-05-31",
  "lang": "he",
  "currency": "ILS",
  "vatType": 0,
  "rounding": true,
  "signed": true,
  "attachment": true,
  "client": {
    "name": "Example Ltd",
    "emails": [
      "finance@example.co.il"
    ],
    "taxId": "515555555",
    "address": "Rothschild 1",
    "city": "Tel Aviv-Yafo",
    "zip": "6100001",
    "country": "IL",
    "phone": "03-5550100",
    "contactPerson": "Noa Levi",
    "paymentTerms": -1,
    "labels": [
      "b2b",
      "monthly"
    ],
    "add": true,
    "self": false
  },
  "income": [
    {
      "catalogNum": "IMPL-001",
      "description": "API implementation services",
      "quantity": 1,
      "price": 8000.0,
      "currency": "ILS",
      "currencyRate": 1.0,
      "vatRate": 0.18,
      "vatType": 0
    },
    {
      "catalogNum": "SUP-001",
      "description": "Production support package",
      "quantity": 2,
      "price": 750.0,
      "currency": "ILS",
      "currencyRate": 1.0,
      "vatRate": 0.18,
      "vatType": 0
    }
  ],
  "discount": {
    "amount": 5,
    "type": "percentage"
  },
  "payment": [
    {
      "type": 4,
      "date": "2026-05-31",
      "price": 10649.5,
      "currency": "ILS",
      "currencyRate": 1.0,
      "bankName": "Bank Leumi",
      "bankBranch": "800",
      "bankAccount": "123456"
    }
  ],
  "linkedDocumentIds": [],
  "linkType": "link"
}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Internal document id. |
| `type` | integer | Document type enum. |
| `number` | integer | Official document number assigned by the system. |
| `status` | integer | Lifecycle status enum. |
| `date` | date | Issue date. |
| `dueDate` | date | Payment due date when present. |
| `currency` | string | Document currency. |
| `subtotal` | number | Total before discount/VAT. |
| `discount` | object | Discount details and calculated total. |
| `taxableTotal` | number | Taxable net total. |
| `vatTaxableTotal` | number | VAT amount. |
| `exemptTotal` | number | VAT-exempt total when present. |
| `total` | number | Final document total. |
| `taxAuthorityAllocationNumber` | string | Present on qualifying B2B tax invoices when allocation succeeds. |
| `client` | object | Client summary. |
| `income` | array | Issued income rows. |
| `payment` | array | Recorded payment rows. |
| `files.downloadLinks` | object | Download links in available languages. |
| `createdAt` | datetime | Creation timestamp. |
| `updatedAt` | datetime | Update timestamp. |

**Response example**

```json
{
  "id": "doc_1001",
  "type": 320,
  "number": 1024,
  "status": 1,
  "date": "2026-05-31",
  "dueDate": "2026-05-31",
  "lang": "he",
  "currency": "ILS",
  "vatType": 0,
  "subtotal": 9500.0,
  "discount": {
    "amount": 5,
    "type": "percentage",
    "total": 475.0
  },
  "taxableTotal": 9025.0,
  "vatTaxableTotal": 1624.5,
  "total": 10649.5,
  "rounding": true,
  "signed": true,
  "client": {
    "id": "cli_2001",
    "name": "Example Ltd",
    "emails": [
      "finance@example.co.il"
    ],
    "taxId": "515555555",
    "country": "IL"
  },
  "income": [
    {
      "catalogNum": "IMPL-001",
      "description": "API implementation services",
      "quantity": 1,
      "price": 8000.0,
      "currency": "ILS",
      "vatRate": 0.18,
      "total": 8000.0
    },
    {
      "catalogNum": "SUP-001",
      "description": "Production support package",
      "quantity": 2,
      "price": 750.0,
      "currency": "ILS",
      "vatRate": 0.18,
      "total": 1500.0
    }
  ],
  "payment": [
    {
      "id": "pay_7001",
      "type": 4,
      "date": "2026-05-31",
      "price": 10649.5,
      "currency": "ILS",
      "bankName": "Bank Leumi",
      "bankBranch": "800",
      "bankAccount": "123456"
    }
  ],
  "files": {
    "signed": true,
    "downloadLinks": {
      "he": "https://www.greeninvoice.co.il/api/v1/documents/download?d=abc123",
      "en": "https://www.greeninvoice.co.il/api/v1/documents/download?d=def456",
      "origin": "https://www.greeninvoice.co.il/api/v1/documents/download?d=ghi789"
    }
  },
  "createdAt": "2026-05-31T10:10:00+03:00",
  "updatedAt": "2026-05-31T10:10:00+03:00"
}
```

### GET /documents/{id} — Get document

Return a full document by id.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| path/header parameters | yes | string | Use path `{id}` when present and `Authorization` for authenticated endpoints. |

**Request example**

```json
{}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Internal document id. |
| `type` | integer | Document type enum. |
| `number` | integer | Official document number assigned by the system. |
| `status` | integer | Lifecycle status enum. |
| `date` | date | Issue date. |
| `dueDate` | date | Payment due date when present. |
| `currency` | string | Document currency. |
| `subtotal` | number | Total before discount/VAT. |
| `discount` | object | Discount details and calculated total. |
| `taxableTotal` | number | Taxable net total. |
| `vatTaxableTotal` | number | VAT amount. |
| `exemptTotal` | number | VAT-exempt total when present. |
| `total` | number | Final document total. |
| `taxAuthorityAllocationNumber` | string | Present on qualifying B2B tax invoices when allocation succeeds. |
| `client` | object | Client summary. |
| `income` | array | Issued income rows. |
| `payment` | array | Recorded payment rows. |
| `files.downloadLinks` | object | Download links in available languages. |
| `createdAt` | datetime | Creation timestamp. |
| `updatedAt` | datetime | Update timestamp. |

**Response example**

```json
{
  "id": "doc_1001",
  "type": 320,
  "number": 1024,
  "status": 1,
  "date": "2026-05-31",
  "dueDate": "2026-05-31",
  "lang": "he",
  "currency": "ILS",
  "vatType": 0,
  "subtotal": 9500.0,
  "discount": {
    "amount": 5,
    "type": "percentage",
    "total": 475.0
  },
  "taxableTotal": 9025.0,
  "vatTaxableTotal": 1624.5,
  "total": 10649.5,
  "rounding": true,
  "signed": true,
  "client": {
    "id": "cli_2001",
    "name": "Example Ltd",
    "emails": [
      "finance@example.co.il"
    ],
    "taxId": "515555555",
    "country": "IL"
  },
  "income": [
    {
      "catalogNum": "IMPL-001",
      "description": "API implementation services",
      "quantity": 1,
      "price": 8000.0,
      "currency": "ILS",
      "vatRate": 0.18,
      "total": 8000.0
    },
    {
      "catalogNum": "SUP-001",
      "description": "Production support package",
      "quantity": 2,
      "price": 750.0,
      "currency": "ILS",
      "vatRate": 0.18,
      "total": 1500.0
    }
  ],
  "payment": [
    {
      "id": "pay_7001",
      "type": 4,
      "date": "2026-05-31",
      "price": 10649.5,
      "currency": "ILS",
      "bankName": "Bank Leumi",
      "bankBranch": "800",
      "bankAccount": "123456"
    }
  ],
  "files": {
    "signed": true,
    "downloadLinks": {
      "he": "https://www.greeninvoice.co.il/api/v1/documents/download?d=abc123",
      "en": "https://www.greeninvoice.co.il/api/v1/documents/download?d=def456",
      "origin": "https://www.greeninvoice.co.il/api/v1/documents/download?d=ghi789"
    }
  },
  "createdAt": "2026-05-31T10:10:00+03:00",
  "updatedAt": "2026-05-31T10:10:00+03:00"
}
```

### POST /documents/search — Search documents

Search documents with filters and pagination.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| `page` | optional | int | Validate according to endpoint semantics and account permissions. |
| `pageSize` | optional | int | Validate according to endpoint semantics and account permissions. |
| `type` | yes | array | Validate according to endpoint semantics and account permissions. |
| `fromDate` | optional | str | Validate according to endpoint semantics and account permissions. |
| `toDate` | optional | str | Validate according to endpoint semantics and account permissions. |
| `clientName` | optional | str | Validate according to endpoint semantics and account permissions. |

**Request example**

```json
{
  "page": 0,
  "pageSize": 25,
  "type": [
    320
  ],
  "fromDate": "2026-05-01",
  "toDate": "2026-05-31",
  "clientName": "Example"
}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `items` | array | Returned by the endpoint. |
| `page` | int | Returned by the endpoint. |
| `pageSize` | int | Returned by the endpoint. |
| `total` | int | Returned by the endpoint. |

**Response example**

```json
{
  "items": [
    {
      "id": "doc_1001",
      "type": 320,
      "number": 1024,
      "status": 1,
      "date": "2026-05-31",
      "clientName": "Example Ltd",
      "total": 10649.5,
      "currency": "ILS"
    }
  ],
  "page": 0,
  "pageSize": 25,
  "total": 1
}
```

### POST /documents/{id}/close — Close document

Close an open document manually or after linked payment.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| `reason` | optional | str | Validate according to endpoint semantics and account permissions. |
| `date` | yes | str | Validate according to endpoint semantics and account permissions. |

**Request example**

```json
{
  "reason": "Paid outside integration",
  "date": "2026-05-31"
}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Returned by the endpoint. |
| `status` | int | Returned by the endpoint. |
| `closedAt` | str | Returned by the endpoint. |

**Response example**

```json
{
  "id": "doc_1001",
  "status": 2,
  "closedAt": "2026-05-31T10:15:00+03:00"
}
```

### GET /documents/{id}/download/links — Get download links

Return signed document download links.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| path/header parameters | yes | string | Use path `{id}` when present and `Authorization` for authenticated endpoints. |

**Request example**

```json
{}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `he` | str | Returned by the endpoint. |
| `en` | str | Returned by the endpoint. |
| `origin` | str | Returned by the endpoint. |

**Response example**

```json
{
  "he": "https://www.greeninvoice.co.il/api/v1/documents/download?d=abc123",
  "en": "https://www.greeninvoice.co.il/api/v1/documents/download?d=def456",
  "origin": "https://www.greeninvoice.co.il/api/v1/documents/download?d=ghi789"
}
```

### POST /documents/{id}/email — Email document

Send a document email using the saved client address or supplied recipients.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| `to` | optional | array | Validate according to endpoint semantics and account permissions. |
| `subject` | optional | str | Validate according to endpoint semantics and account permissions. |
| `message` | optional | str | Validate according to endpoint semantics and account permissions. |

**Request example**

```json
{
  "to": [
    "finance@example.co.il"
  ],
  "subject": "חשבונית מס/קבלה 1024",
  "message": "שלום, מצורפת חשבונית מס/קבלה עבור השירות."
}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Returned by the endpoint. |
| `sent` | bool | Returned by the endpoint. |
| `recipients` | array | Returned by the endpoint. |
| `sentAt` | str | Returned by the endpoint. |

**Response example**

```json
{
  "id": "doc_1001",
  "sent": true,
  "recipients": [
    "finance@example.co.il"
  ],
  "sentAt": "2026-05-31T10:20:00+03:00"
}
```

### POST /clients — Create client

Create a client record.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| `name` | yes | str | Validate according to endpoint semantics and account permissions. |
| `emails` | optional | array | Validate according to endpoint semantics and account permissions. |
| `taxId` | optional | str | Validate according to endpoint semantics and account permissions. |
| `address` | optional | str | Validate according to endpoint semantics and account permissions. |
| `city` | optional | str | Validate according to endpoint semantics and account permissions. |
| `zip` | optional | str | Validate according to endpoint semantics and account permissions. |
| `country` | optional | str | Validate according to endpoint semantics and account permissions. |
| `active` | optional | bool | Validate according to endpoint semantics and account permissions. |
| `paymentTerms` | optional | int | Validate according to endpoint semantics and account permissions. |
| `labels` | optional | array | Validate according to endpoint semantics and account permissions. |

**Request example**

```json
{
  "name": "Example Ltd",
  "emails": [
    "finance@example.co.il"
  ],
  "taxId": "515555555",
  "address": "Rothschild 1",
  "city": "Tel Aviv-Yafo",
  "zip": "6100001",
  "country": "IL",
  "active": true,
  "paymentTerms": 30,
  "labels": [
    "b2b"
  ]
}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Returned by the endpoint. |
| `name` | str | Returned by the endpoint. |
| `emails` | array | Returned by the endpoint. |
| `active` | bool | Returned by the endpoint. |
| `taxId` | str | Returned by the endpoint. |
| `country` | str | Returned by the endpoint. |
| `createdAt` | str | Returned by the endpoint. |

**Response example**

```json
{
  "id": "cli_2001",
  "name": "Example Ltd",
  "emails": [
    "finance@example.co.il"
  ],
  "active": true,
  "taxId": "515555555",
  "country": "IL",
  "createdAt": "2026-05-31T09:00:00+03:00"
}
```

### GET /clients/{id} — Get client

Return a client by id.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| path/header parameters | yes | string | Use path `{id}` when present and `Authorization` for authenticated endpoints. |

**Request example**

```json
{}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Returned by the endpoint. |
| `name` | str | Returned by the endpoint. |
| `emails` | array | Returned by the endpoint. |
| `active` | bool | Returned by the endpoint. |
| `taxId` | str | Returned by the endpoint. |
| `country` | str | Returned by the endpoint. |

**Response example**

```json
{
  "id": "cli_2001",
  "name": "Example Ltd",
  "emails": [
    "finance@example.co.il"
  ],
  "active": true,
  "taxId": "515555555",
  "country": "IL"
}
```

### PUT /clients/{id} — Update client

Update mutable client fields.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| `name` | yes | str | Validate according to endpoint semantics and account permissions. |
| `emails` | optional | array | Validate according to endpoint semantics and account permissions. |
| `active` | optional | bool | Validate according to endpoint semantics and account permissions. |
| `paymentTerms` | optional | int | Validate according to endpoint semantics and account permissions. |
| `labels` | optional | array | Validate according to endpoint semantics and account permissions. |

**Request example**

```json
{
  "name": "Example Ltd",
  "emails": [
    "finance@example.co.il",
    "bookkeeping@example.co.il"
  ],
  "active": true,
  "paymentTerms": 45,
  "labels": [
    "b2b",
    "priority"
  ]
}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Returned by the endpoint. |
| `name` | str | Returned by the endpoint. |
| `emails` | array | Returned by the endpoint. |
| `paymentTerms` | int | Returned by the endpoint. |
| `labels` | array | Returned by the endpoint. |

**Response example**

```json
{
  "id": "cli_2001",
  "name": "Example Ltd",
  "emails": [
    "finance@example.co.il",
    "bookkeeping@example.co.il"
  ],
  "paymentTerms": 45,
  "labels": [
    "b2b",
    "priority"
  ]
}
```

### DELETE /clients/{id} — Delete client

Delete or deactivate a client record when allowed.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| path/header parameters | yes | string | Use path `{id}` when present and `Authorization` for authenticated endpoints. |

**Request example**

```json
{}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Returned by the endpoint. |
| `deleted` | bool | Returned by the endpoint. |

**Response example**

```json
{
  "id": "cli_2001",
  "deleted": true
}
```

### POST /clients/search — Search clients

Search clients with filters and pagination.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| `name` | yes | str | Validate according to endpoint semantics and account permissions. |
| `email` | optional | str | Validate according to endpoint semantics and account permissions. |
| `active` | optional | bool | Validate according to endpoint semantics and account permissions. |
| `page` | optional | int | Validate according to endpoint semantics and account permissions. |
| `pageSize` | optional | int | Validate according to endpoint semantics and account permissions. |

**Request example**

```json
{
  "name": "Example",
  "email": "finance@example.co.il",
  "active": true,
  "page": 0,
  "pageSize": 25
}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `items` | array | Returned by the endpoint. |
| `page` | int | Returned by the endpoint. |
| `pageSize` | int | Returned by the endpoint. |
| `total` | int | Returned by the endpoint. |

**Response example**

```json
{
  "items": [
    {
      "id": "cli_2001",
      "name": "Example Ltd",
      "emails": [
        "finance@example.co.il"
      ],
      "active": true
    }
  ],
  "page": 0,
  "pageSize": 25,
  "total": 1
}
```

### POST /clients/{id}/assoc — Associate client

Associate existing documents to a client.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| `documentIds` | optional | array | Validate according to endpoint semantics and account permissions. |

**Request example**

```json
{
  "documentIds": [
    "doc_1001",
    "doc_1002"
  ]
}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `clientId` | str | Returned by the endpoint. |
| `documentIds` | array | Returned by the endpoint. |
| `associated` | int | Returned by the endpoint. |

**Response example**

```json
{
  "clientId": "cli_2001",
  "documentIds": [
    "doc_1001",
    "doc_1002"
  ],
  "associated": 2
}
```

### POST /items — Create item

Create a catalog item.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| `catalogNum` | optional | str | Validate according to endpoint semantics and account permissions. |
| `description` | optional | str | Validate according to endpoint semantics and account permissions. |
| `price` | optional | float | Validate according to endpoint semantics and account permissions. |
| `currency` | optional | str | Validate according to endpoint semantics and account permissions. |
| `vatType` | optional | int | Validate according to endpoint semantics and account permissions. |
| `active` | optional | bool | Validate according to endpoint semantics and account permissions. |

**Request example**

```json
{
  "catalogNum": "CONSULT-HOUR",
  "description": "Consulting hour",
  "price": 450.0,
  "currency": "ILS",
  "vatType": 0,
  "active": true
}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Returned by the endpoint. |
| `catalogNum` | str | Returned by the endpoint. |
| `description` | str | Returned by the endpoint. |
| `price` | float | Returned by the endpoint. |
| `currency` | str | Returned by the endpoint. |
| `active` | bool | Returned by the endpoint. |

**Response example**

```json
{
  "id": "itm_3001",
  "catalogNum": "CONSULT-HOUR",
  "description": "Consulting hour",
  "price": 450.0,
  "currency": "ILS",
  "active": true
}
```

### GET /items/{id} — Get item

Return a catalog item.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| path/header parameters | yes | string | Use path `{id}` when present and `Authorization` for authenticated endpoints. |

**Request example**

```json
{}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Returned by the endpoint. |
| `catalogNum` | str | Returned by the endpoint. |
| `description` | str | Returned by the endpoint. |
| `price` | float | Returned by the endpoint. |
| `currency` | str | Returned by the endpoint. |
| `active` | bool | Returned by the endpoint. |

**Response example**

```json
{
  "id": "itm_3001",
  "catalogNum": "CONSULT-HOUR",
  "description": "Consulting hour",
  "price": 450.0,
  "currency": "ILS",
  "active": true
}
```

### PUT /items/{id} — Update item

Update catalog item fields.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| `description` | optional | str | Validate according to endpoint semantics and account permissions. |
| `price` | optional | float | Validate according to endpoint semantics and account permissions. |
| `currency` | optional | str | Validate according to endpoint semantics and account permissions. |
| `active` | optional | bool | Validate according to endpoint semantics and account permissions. |

**Request example**

```json
{
  "description": "Senior consulting hour",
  "price": 520.0,
  "currency": "ILS",
  "active": true
}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Returned by the endpoint. |
| `description` | str | Returned by the endpoint. |
| `price` | float | Returned by the endpoint. |
| `currency` | str | Returned by the endpoint. |
| `active` | bool | Returned by the endpoint. |

**Response example**

```json
{
  "id": "itm_3001",
  "description": "Senior consulting hour",
  "price": 520.0,
  "currency": "ILS",
  "active": true
}
```

### POST /items/search — Search items

Search catalog items.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| `description` | optional | str | Validate according to endpoint semantics and account permissions. |
| `active` | optional | bool | Validate according to endpoint semantics and account permissions. |
| `page` | optional | int | Validate according to endpoint semantics and account permissions. |
| `pageSize` | optional | int | Validate according to endpoint semantics and account permissions. |

**Request example**

```json
{
  "description": "consulting",
  "active": true,
  "page": 0,
  "pageSize": 25
}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `items` | array | Returned by the endpoint. |
| `page` | int | Returned by the endpoint. |
| `pageSize` | int | Returned by the endpoint. |
| `total` | int | Returned by the endpoint. |

**Response example**

```json
{
  "items": [
    {
      "id": "itm_3001",
      "catalogNum": "CONSULT-HOUR",
      "description": "Consulting hour",
      "price": 450.0
    }
  ],
  "page": 0,
  "pageSize": 25,
  "total": 1
}
```

### GET /webhooks — List webhooks

List registered webhooks for the active business.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| path/header parameters | yes | string | Use path `{id}` when present and `Authorization` for authenticated endpoints. |

**Request example**

```json
{}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `items` | array | Returned by the endpoint. |

**Response example**

```json
{
  "items": [
    {
      "id": "wh_4001",
      "url": "https://example.com/green-invoice/webhook",
      "events": [
        "document.created"
      ],
      "active": true,
      "createdAt": "2026-05-30T12:00:00+03:00"
    }
  ]
}
```

### POST /webhooks — Register webhook

Register a webhook endpoint.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| `url` | yes | str | Validate according to endpoint semantics and account permissions. |
| `events` | optional | array | Validate according to endpoint semantics and account permissions. |
| `secret` | yes | str | Validate according to endpoint semantics and account permissions. |
| `active` | optional | bool | Validate according to endpoint semantics and account permissions. |

**Request example**

```json
{
  "url": "https://example.com/green-invoice/webhook",
  "events": [
    "document.created",
    "document.updated"
  ],
  "secret": "shared-signing-secret",
  "active": true
}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Returned by the endpoint. |
| `url` | str | Returned by the endpoint. |
| `events` | array | Returned by the endpoint. |
| `active` | bool | Returned by the endpoint. |

**Response example**

```json
{
  "id": "wh_4001",
  "url": "https://example.com/green-invoice/webhook",
  "events": [
    "document.created",
    "document.updated"
  ],
  "active": true
}
```

### DELETE /webhooks/{id} — Delete webhook

Delete a webhook registration.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| path/header parameters | yes | string | Use path `{id}` when present and `Authorization` for authenticated endpoints. |

**Request example**

```json
{}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Returned by the endpoint. |
| `deleted` | bool | Returned by the endpoint. |

**Response example**

```json
{
  "id": "wh_4001",
  "deleted": true
}
```

### POST /expenses — Create expense

Create an expense record.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| `date` | yes | str | Validate according to endpoint semantics and account permissions. |
| `description` | optional | str | Validate according to endpoint semantics and account permissions. |
| `amount` | optional | float | Validate according to endpoint semantics and account permissions. |
| `currency` | optional | str | Validate according to endpoint semantics and account permissions. |
| `vat` | optional | float | Validate according to endpoint semantics and account permissions. |
| `supplierName` | optional | str | Validate according to endpoint semantics and account permissions. |
| `supplierTaxId` | optional | str | Validate according to endpoint semantics and account permissions. |
| `category` | optional | int | Validate according to endpoint semantics and account permissions. |

**Request example**

```json
{
  "date": "2026-05-31",
  "description": "Office supplies",
  "amount": 236.0,
  "currency": "ILS",
  "vat": 36.0,
  "supplierName": "Office Store",
  "supplierTaxId": "514444444",
  "category": 0
}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Returned by the endpoint. |
| `date` | str | Returned by the endpoint. |
| `description` | str | Returned by the endpoint. |
| `amount` | float | Returned by the endpoint. |
| `currency` | str | Returned by the endpoint. |
| `vat` | float | Returned by the endpoint. |
| `status` | str | Returned by the endpoint. |

**Response example**

```json
{
  "id": "exp_5001",
  "date": "2026-05-31",
  "description": "Office supplies",
  "amount": 236.0,
  "currency": "ILS",
  "vat": 36.0,
  "status": "recorded"
}
```

### GET /expenses/{id} — Get expense

Return an expense by id.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| path/header parameters | yes | string | Use path `{id}` when present and `Authorization` for authenticated endpoints. |

**Request example**

```json
{}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `id` | str | Returned by the endpoint. |
| `date` | str | Returned by the endpoint. |
| `description` | str | Returned by the endpoint. |
| `amount` | float | Returned by the endpoint. |
| `currency` | str | Returned by the endpoint. |
| `vat` | float | Returned by the endpoint. |
| `status` | str | Returned by the endpoint. |

**Response example**

```json
{
  "id": "exp_5001",
  "date": "2026-05-31",
  "description": "Office supplies",
  "amount": 236.0,
  "currency": "ILS",
  "vat": 36.0,
  "status": "recorded"
}
```

### POST /expenses/search — Search expenses

Search expenses with filters and pagination.

**Parameters and validation**

| Parameter | Required | Type | Validation |
|---|---:|---|---|
| `fromDate` | optional | str | Validate according to endpoint semantics and account permissions. |
| `toDate` | optional | str | Validate according to endpoint semantics and account permissions. |
| `supplierName` | optional | str | Validate according to endpoint semantics and account permissions. |
| `page` | optional | int | Validate according to endpoint semantics and account permissions. |
| `pageSize` | optional | int | Validate according to endpoint semantics and account permissions. |

**Request example**

```json
{
  "fromDate": "2026-05-01",
  "toDate": "2026-05-31",
  "supplierName": "Office",
  "page": 0,
  "pageSize": 25
}
```

**Response fields**

| Field | Type | Meaning |
|---|---|---|
| `items` | array | Returned by the endpoint. |
| `page` | int | Returned by the endpoint. |
| `pageSize` | int | Returned by the endpoint. |
| `total` | int | Returned by the endpoint. |

**Response example**

```json
{
  "items": [
    {
      "id": "exp_5001",
      "date": "2026-05-31",
      "description": "Office supplies",
      "amount": 236.0,
      "currency": "ILS"
    }
  ],
  "page": 0,
  "pageSize": 25,
  "total": 1
}
```


## Payment method code note

The legacy document-creation payloads in this package retain numeric payment type examples (`1` cash, `2` check, `3` credit card, `4` bank transfer, and so on). The live public webhook payload documentation currently exposes payment methods as strings under `paymentMethod.type`, for example `wire-transfer`. Treat numeric payment codes as legacy create-payload enums and validate against the current endpoint documentation before introducing new payment channels.

## Pagination semantics

Search endpoints accept `page` and `pageSize` in the request body. Use zero-based page indexes. Use conservative `pageSize` values such as 25 or 50 unless the current developer documentation for the endpoint states a higher maximum. Continue while `items` is non-empty and either `total` indicates more records or the returned item count equals `pageSize`.

Example:

```json
{
  "page": 0,
  "pageSize": 100,
  "fromDate": "2026-05-01",
  "toDate": "2026-05-31"
}
```

Store the last successfully processed page and search filter in batch jobs. When exporting documents for bookkeeping, prefer immutable date windows and repeat the final page once before closing the job.

## Request schemas

### Document payload

| Field | Required | Type | Notes |
|---|---:|---|---|
| `type` | yes | integer | Document type enum. |
| `date` | yes | string | `YYYY-MM-DD`. |
| `dueDate` | conditional | string | Required when payment is due later. |
| `lang` | optional | string | `he` or `en`. |
| `currency` | optional | string | Default is usually account currency; send explicitly. |
| `vatType` | optional | integer | 0 default, 1 exempt, 2 mixed. |
| `client.id` | conditional | string | Use for existing client. |
| `client.name` | conditional | string | Required for new client. |
| `client.emails` | recommended | array[string] | Required for emailing. |
| `client.taxId` | recommended for B2B | string | Critical for Israeli B2B and allocation checks. |
| `client.add` | optional | boolean | Save new client while creating document. |
| `income[].description` | conditional | string | Required for income rows. |
| `income[].quantity` | conditional | number | Positive quantity; use clear quantity for services and goods. |
| `income[].price` | conditional | number | Unit price in row currency. |
| `income[].currency` | optional | string | Match document or specify row currency. |
| `income[].currencyRate` | optional | number | Use for fixed exchange rate. |
| `income[].vatRate` | optional | number | Example `0.18` for 18%. |
| `income[].vatType` | optional | integer | 0 default, 1 VAT included, 2 exempt. |
| `payment[].type` | conditional | integer | Payment type enum. |
| `payment[].date` | conditional | string | Payment date. |
| `payment[].price` | conditional | number | Payment amount. |
| `payment[].currency` | optional | string | Payment currency. |
| `discount.amount` | optional | number | Discount amount. |
| `discount.type` | optional | string | `sum` or `percentage`. |
| `linkedDocumentIds` | optional | array[string] | Link, close, or cancel related documents. |
| `linkType` | optional | string | `link` or `cancel`. |

### Client payload

| Field | Required | Type | Notes |
|---|---:|---|---|
| `name` | yes | string | Legal or display name. |
| `emails` | recommended | array[string] | Accounting recipient list. |
| `active` | optional | boolean | Active client flag. |
| `taxId` | recommended for B2B | string | Israeli עוסק/ח.פ. or foreign tax id. |
| `accountingKey` | optional | string | External bookkeeping key. |
| `paymentTerms` | optional | integer | Payment terms enum. |
| `address`, `city`, `zip`, `country` | optional | string | Billing address. |
| `phone`, `mobile`, `fax` | optional | string | Contact details. |
| `contactPerson` | optional | string | Main contact. |
| `labels` | optional | array[string] | Operational labels. |

### Item payload

| Field | Required | Type | Notes |
|---|---:|---|---|
| `catalogNum` | optional | string | SKU or catalog number. |
| `description` | yes | string | Item description. |
| `price` | yes | number | Unit price. |
| `currency` | optional | string | Currency enum. |
| `vatType` | optional | integer | Default or exempt handling. |
| `active` | optional | boolean | Hide obsolete catalog entries by setting inactive. |

### Expense payload

| Field | Required | Type | Notes |
|---|---:|---|---|
| `date` | yes | string | Expense date. |
| `description` | yes | string | Description. |
| `amount` | yes | number | Gross amount. |
| `currency` | optional | string | Currency enum. |
| `vat` | optional | number | VAT amount if deductible. |
| `supplierName` | recommended | string | Supplier legal name. |
| `supplierTaxId` | recommended | string | Supplier עוסק/ח.פ. |
| `category` | optional | integer | Account category enum. |

## Response object fields

### Document response

| Field | Type | Meaning |
|---|---|---|
| `id` | string | Internal id. |
| `type` | integer | Document type. |
| `number` | integer | Official assigned number. |
| `status` | integer | Document status. |
| `date` | string | Issue date. |
| `dueDate` | string | Due date when present. |
| `currency` | string | Currency. |
| `subtotal` | number | Sum before discount and VAT. |
| `discount` | object | Discount details. |
| `taxableTotal` | number | Taxable net. |
| `exemptTotal` | number | Exempt net when present. |
| `vatTaxableTotal` | number | VAT amount. |
| `total` | number | Final total. |
| `taxAuthorityAllocationNumber` | string | Allocation number for qualifying invoices when returned. |
| `client` | object | Client summary. |
| `income` | array | Income rows. |
| `payment` | array | Payment rows. |
| `linkedDocumentIds` | array | Linked documents. |
| `files.downloadLinks` | object | Download URLs. |
| `createdAt` | string | Creation time. |
| `updatedAt` | string | Update time. |

## Enum reference

### Document types

| Code | Hebrew | English | Operational use |
|---:|---|---|---|
| 10 | הצעת מחיר | Price Quote | Commercial offer before commitment; no accounting effect until accepted. |
| 100 | הזמנה | Order | Customer order confirmation before delivery or invoicing. |
| 200 | תעודת משלוח | Delivery Note | Goods shipment without immediate tax invoice. |
| 210 | תעודת החזרה | Return Note | Return of goods that were delivered. |
| 300 | חשבון עסקה | Transaction Invoice | Payment demand or pro forma-like billing request; not a VAT invoice. |
| 305 | חשבונית מס | Tax Invoice | VAT invoice for B2B/B2C sale where payment will be collected later. |
| 320 | חשבונית מס/קבלה | Tax Invoice-Receipt | Combined VAT invoice and receipt when payment is received at issue time. |
| 330 | חשבונית זיכוי | Credit Note | Cancels or reduces a previous tax invoice or tax invoice-receipt. |
| 400 | קבלה | Receipt | Receipt for payment against an existing invoice or non-VAT payment event. |
| 405 | קבלה על תרומה | Donation Receipt | Receipt for donation income for eligible non-profit entities. |
| 500 | הזמנת רכש | Purchase Order | Purchase order sent to a supplier. |
| 600 | קבלת פיקדון | Deposit Receipt | Receipt for a deposit or prepayment held before revenue recognition. |
| 610 | משיכת פיקדון | Deposit Withdrawal | Withdrawal or application of a previous deposit. |

### Document statuses

| Code | Meaning | Handling |
|---:|---|---|
| 0 | Open | Awaiting payment, closure, or later lifecycle action. |
| 1 | Closed | Fully paid or completed. |
| 2 | Manually closed | Closed by explicit operation. |
| 3 | Canceling other document | Credit/cancellation document. |
| 4 | Canceled | Original document cancelled by a linked document. |

### Payment types

| Code | Hebrew | English | Handling |
|---:|---|---|---|
| -1 | לא שולם | Unpaid | Use only as an explicit unpaid marker where supported. |
| 0 | ניכוי במקור | Withholding Tax | Tax withheld by payer; record alongside actual cash/bank/card payment. |
| 1 | מזומן | Cash | Cash payment. |
| 2 | המחאה | Check | Check payment; include bank and check details. |
| 3 | כרטיס אשראי | Credit Card | Credit/debit card transaction; include card/deal fields when known. |
| 4 | העברה בנקאית | Bank Transfer | Bank transfer or wire. |
| 5 | פייפאל | PayPal | PayPal payment. |
| 10 | אפליקציית תשלום | Payment App | Bit, PayBox, or legacy app payment with appType. |
| 11 | אחר | Other | Fallback when the payment channel has no dedicated enum. |

### Payment sub-types

| Code | Name | Handling |
|---:|---|---|
| 1 | Bitcoin | Use only if the account accepts crypto-style records. |
| 2 | Money equivalent | Use for voucher or equivalent value. |
| 3 | V-Check | Use for virtual check flows. |

### Payment app types

| Code | Name | Handling |
|---:|---|---|
| 1 | Bit | Active payment app value. |
| 2 | Pepper Pay | Legacy value; avoid for new payments. |
| 3 | PayBox | Active payment app value. |

### Credit card types

| Code | Name |
|---:|---|
| 0 | Unknown |
| 1 | Isracard |
| 2 | Visa |
| 3 | Mastercard |
| 4 | American Express |
| 5 | Diners |

### Credit card deal types

| Code | Hebrew | English |
|---:|---|---|
| 1 | רגיל | Regular |
| 2 | תשלומים | Installments |
| 3 | קרדיט | Credit |
| 4 | חיוב נדחה | Deferred |
| 5 | אחר | Other |

### VAT types

| Context | Code | Meaning |
|---|---:|---|
| Document | 0 | Default based on account and document. |
| Document | 1 | Exempt. |
| Document | 2 | Mixed VAT treatment. |
| Income row | 0 | Default. |
| Income row | 1 | VAT included in row price. |
| Income row | 2 | Exempt row. |

### Business types

| Code | Hebrew | English |
|---:|---|---|
| 1 | עוסק מורשה | Licensed Dealer |
| 2 | חברה בע״מ | Ltd. Company |
| 3 | עוסק פטור | Exempt Dealer |
| 4 | עמותה | Non-Profit |
| 5 | חברה לתועלת הציבור | Public Benefit Company |
| 6 | שותפות | Partnership |

### Payment terms

| Code | Meaning |
|---:|---|
| -1 | Immediate |
| 0 | End of month |
| 10 | End of month + 10 |
| 15 | End of month + 15 |
| 30 | End of month + 30 |
| 45 | End of month + 45 |
| 60 | End of month + 60 |
| 75 | End of month + 75 |
| 90 | End of month + 90 |
| 120 | End of month + 120 |

### Supported currencies

`ILS`, `USD`, `EUR`, `GBP`, `JPY`, `CHF`, `CNY`, `AUD`, `CAD`, `RUB`, `BRL`, `HKD`, `SGD`, `THB`, `MXN`, `TRY`, `NZD`, `SEK`, `NOK`, `DKK`, `KRW`, `INR`, `IDR`, `PLN`, `RON`, `ZAR`, `HRK`.

## Error-code reference

| HTTP | Typical body shape | Meaning | Suggested handling |
|---:|---|---|---|
| 400 | `{"error":"bad_request","message":"Invalid JSON"}` | Malformed JSON or unsupported request shape | Fix serializer and content type. |
| 401 | `{"error":"unauthorized","message":"Invalid or expired token"}` | Missing, invalid, or expired bearer token | Refresh token once; then require new credentials. |
| 403 | `{"error":"forbidden","message":"Permission denied"}` | Plan, role, business, or feature gate | Stop retries; surface access problem. |
| 404 | `{"error":"not_found","message":"Document not found"}` | Id not found in the active business/environment | Verify id, business, and sandbox/production environment. |
| 409 | `{"error":"conflict","message":"Document already closed"}` | Lifecycle conflict or duplicate state transition | Read current document and reconcile state. |
| 422 | `{"error":"validation_error","fields":{"client.taxId":"Invalid tax id"}}` | Business validation failure | Show field-level error and correct payload. |
| 429 | `{"error":"rate_limited","message":"Too many requests"}` | Rate limit | Respect `Retry-After`, back off with jitter. |
| 500 | `{"error":"server_error","message":"Unexpected error"}` | Server failure | Retry safe operations; queue writes and reconcile before replay. |
| 502 | `{"error":"bad_gateway","message":"Upstream unavailable"}` | Temporary upstream issue | Retry with backoff. |
| 503 | `{"error":"service_unavailable","message":"Maintenance"}` | Maintenance or overload | Retry after delay and alert if persistent. |

## webhooks

### Event types

| Event | Payload | Typical handling |
|---|---|---|
| `document.created` | Full document summary | Store id, number, totals, download links, allocation number. |
| `document.updated` | Changed document summary | Re-read document before mutating local records. |
| `document.closed` | Document id and status | Mark receivable closed. |
| `document.canceled` | Original and canceling document ids | Link credit/cancellation records. |
| `payment.created` | Payment row details | Reconcile receipts and open invoices. |
| `client.created` | Client summary | Upsert client cache. |
| `client.updated` | Client summary | Update local client cache. |
| `expense.created` | Expense summary | Route to expense approval/export. |
| `expense.updated` | Expense summary | Update local expense cache. |

### Payload shape

```json
{
  "event": "document.created",
  "id": "evt_6001",
  "createdAt": "2026-05-31T10:10:05+03:00",
  "businessId": "biz_9a10",
  "data": {
  "id": "doc_1001",
  "type": 320,
  "number": 1024,
  "status": 1,
  "date": "2026-05-31",
  "dueDate": "2026-05-31",
  "lang": "he",
  "currency": "ILS",
  "vatType": 0,
  "subtotal": 9500.0,
  "discount": {
    "amount": 5,
    "type": "percentage",
    "total": 475.0
  },
  "taxableTotal": 9025.0,
  "vatTaxableTotal": 1624.5,
  "total": 10649.5,
  "rounding": true,
  "signed": true,
  "client": {
    "id": "cli_2001",
    "name": "Example Ltd",
    "emails": [
      "finance@example.co.il"
    ],
    "taxId": "515555555",
    "country": "IL"
  },
  "income": [
    {
      "catalogNum": "IMPL-001",
      "description": "API implementation services",
      "quantity": 1,
      "price": 8000.0,
      "currency": "ILS",
      "vatRate": 0.18,
      "total": 8000.0
    },
    {
      "catalogNum": "SUP-001",
      "description": "Production support package",
      "quantity": 2,
      "price": 750.0,
      "currency": "ILS",
      "vatRate": 0.18,
      "total": 1500.0
    }
  ],
  "payment": [
    {
      "id": "pay_7001",
      "type": 4,
      "date": "2026-05-31",
      "price": 10649.5,
      "currency": "ILS",
      "bankName": "Bank Leumi",
      "bankBranch": "800",
      "bankAccount": "123456"
    }
  ],
  "files": {
    "signed": true,
    "downloadLinks": {
      "he": "https://www.greeninvoice.co.il/api/v1/documents/download?d=abc123",
      "en": "https://www.greeninvoice.co.il/api/v1/documents/download?d=def456",
      "origin": "https://www.greeninvoice.co.il/api/v1/documents/download?d=ghi789"
    }
  },
  "createdAt": "2026-05-31T10:10:00+03:00",
  "updatedAt": "2026-05-31T10:10:00+03:00"
}
}
```

### Signature verification

Use the exact raw request body bytes and the shared webhook secret. Compare the received signature with HMAC-SHA256 using constant-time comparison. The bundled client supports plain hex signatures and `sha256=<hex>` signatures.

## Official documentation

- https://www.greeninvoice.co.il/api-docs/
- https://app.greeninvoice.co.il/api
- https://www.greeninvoice.co.il/help-center/generating-api-key/
- https://www.greeninvoice.co.il/help-center/developers/tax-auth-connect/
- https://www.greeninvoice.co.il/magazine/israel-invoice/
- https://www.greeninvoice.co.il/magazine/webhooks/
