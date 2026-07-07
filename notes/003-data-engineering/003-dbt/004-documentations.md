---
title: Documentations
---
## Types of Documentation

The documentation that you can manage with dbt is vast. The goal is to make documentation for components of data governance: Data Catalog & Glossary, Data Contracts & Schema Registries, Data Lineage, Security & Acess Control Policies.

### Data Catalog & Glossary

- Business Glossary: Define standard business terms (e.g., what exactly constitutes an "Active User"?). 
	- `semantic layer`
- Data Dictionary: Map columns, data types, and descriptions for every core table or collection.
	- `_model.yml`

### Data Contracts & Schema Registries

- Data Contract: [Open Data Contract Standard (ODCS)](https://datacontract.com/)
	- `dbt model contracts`
	- Fundamentals: Every data contract starts with its fundamentals: the version of the standard, unique identifier, name, data contract version number, and status. This metadata identifies the contract and enables versioning.
	- Schema: The schema defines the structure and semantics of your data. Here we define the table structure with its columns. Each property includes technical details, business semantics, and governance attributes.
	- Data Quality: Data quality rules ensure that data meets expectations. Define checks like valid value constraints, row count thresholds, and custom SQL validation logic. These can be tested automatically with the Data Contract CLI.
	- Team: Document who owns and maintains the data contract. Include team name, description, and members with their roles. Add support channels, how data consumers can reach out to the owners.
	- Terms of Use: Define the purpose, usage guidelines, and limitations for your data. This helps consumers understand what they can and cannot do with the data, establishing clear governance boundaries.
	- SLAs: Service Level Agreements define non-functional guarantees. Data consumers can match these with their use-case requirements.
	- Servers: Finally, specify where the data lives. The server configuration includes connection details for different environments.

```yaml
# Fundamentals
apiVersion: v3.1.0
kind: DataContract
id: orders
name: Orders
version: 1.0.0
status: active

# Terms of Use
description:
  purpose: "Provides order and line item data for analytics and reporting"
  usage: "Used by analytics team for sales analysis and business intelligence"
  limitations: "Contains only the last 2 years of data"
  customProperties:
    - property: "sensitivity"
      value: "secret"
      description: "Data contains personally identifiable information"
  authoritativeDefinitions:
    - url: "https://entropy-data.com/policies/gdpr-compliance"
      type: "businessDefinition"
      description: "GDPR compliance policy for handling customer data"

# Schema & Quality
schema:
  - name: orders
    physicalType: TABLE
    description: All historic web shop orders since 2020-01-01. Includes successful and cancelled orders.
    properties:
      - name: order_id
        logicalType: string
        description: The internal order id for every orders. Do not show this to a customer.
        businessName: Internal Order ID
        physicalType: UUID
        examples:
          - 99e8bb10-3785-4634-9664-8dc79eb69d43
        primaryKey: true
        classification: internal
        required: true
        unique: true
      - name: customer_id
        logicalType: string
        description: A reference to the customer number
        businessName: Customer Number
        physicalType: TEXT
        examples:
          - c123456789
        required: true
        unique: false
        logicalTypeOptions:
          minLength: 10
          maxLength: 10
        tags:
          - pii:true
        classification: internal
        criticalDataElement: true
      - name: order_total
        logicalType: integer
        description: The order total amount in cents, including tax, after discounts.
          Includes shipping costs.
        physicalType: INTEGER
        examples:
          - "9999"
        quality:
          - type: text
            description: The order_total equals the sum of all related line items.
        required: true
        businessName: Order Amount
      - name: order_timestamp
        logicalType: timestamp
        description: The time including timezone when the order payment was successfully
          confirmed.
        physicalType: TIMESTAMPTZ
        businessName: Order Date
        examples:
          - "2025-03-01 14:30:00+01"
      - name: order_status
        businessName: Status
        description: The business status of the order
        logicalType: string
        physicalType: TEXT
        examples:
          - shipped
        quality:
          - type: library
            description: Ensure that there are no other status values.
            metric: invalidValues
            arguments:
              validValues:
                - pending
                - paid
                - processing
                - shipped
                - delivered
                - cancelled
                - refunded
            mustBe: 0
    quality:
      - type: library
        metric: rowCount
        mustBeGreaterThan: 100000
        description: If there are less than 100k rows, something is wrong.
  - name: line_items
    physicalType: table
    description: Details for each item in an order
    properties:
      - name: line_item_id
        logicalType: string
        description: Unique identifier for the line item
        physicalType: UUID
        examples:
          - 12c9ba21-0c44-4e29-ba72-b8fd01c1be30
        logicalTypeOptions:
          format: uuid
        required: true
        primaryKey: true
      - name: sku
        logicalType: string
        businessName: Stock Keeping Unit
        description: Identifier for the purchased product
        physicalType: TEXT
        examples:
          - 111222333
        required: true
      - name: price
        logicalType: integer
        description: Price in cents for this line item including tax
        physicalType: INTEGER
        examples:
          - 9999
        required: true
      - name: order_id
        required: false
        primaryKey: false
        logicalType: string
        physicalType: UUID
        relationships:
          - type: foreignKey
            to: orders.order_id
            
# Servers
servers:
  - server: production
    environment: prod
    type: postgres
    host: aws-1-eu-central-2.pooler.supabase.com
    port: 6543
    database: postgres
    schema: dp_orders_v1
    
# Team
team:
  name: sales
  description: This data product is owned by the "Sales" team
  members:
    - username: john@example.com
      name: John Doe
      role: Owner
  authoritativeDefinitions:
    - type: slack
      url: https://slack.example.com/teams/sales
roles:
  - role: analyst_us
    description: Read access for analytics to US orders
  - role: analyst_eu
    description: Read access for analytics to EU orders
    
# SLAs
slaProperties:
  - property: availability
    value: 99.9%
    description: Data platform uptime guarantee
  - property: retention
    value: "1"
    unit: year
    description: Data will be deleted after 1 year
  - property: freshness
    value: "24"
    unit: hours
#    element: orders.order_timestamp # enable this to check freshness with Data Contract CLI
    description: Within 24 hours of order placement
  - property: support
    value: business hours
    description: Support only during business hours
price:
  priceAmount: 0
  priceCurrency: USD
  priceUnit: monthly
tags:
  - e-commerce
  - transactions
  - pii
customProperties:
  - property: dataPlatformRole
    value: role_orders_v1
contractCreatedTs: "2025-01-15T10:00:00Z"
```
### Data Lineage

- Upstream & Downstream Mapping: Visual or code-based mapping showing exactly how data flows from your source backend APIs, through orchestration pipelines (like Airflow), to final analytical tables or LLM embedding stores.
	- `dbt docs generate && dbt docs serve` automatically does it, but let's add on how to filter for these

### Security & Access Control Policies

- Classification: Tag data assets by sensitivity (e.g., Public, Internal, Confidential, PII).
- RBAC/ABAC Matrix: Document who has access to what, and enforce masking or tokenization for sensitive fields.
	- let's make a preconfigured sql queries to make this happen (RBAC matrix queries)
	- `dbt_project.yml`
```
+grants:
	select: ['ROLES']
	references: ['ROLES']
```

## Generate Documentations

```shell
dbt docs generate
```

> [!note]
> The command to generate the docs will change in future releases.
> `dbt compile --write-index --static-analysis strict`

## Serve Documentations

```shell
dbt docs serve
```

***

[Last modified: 2026-07-02]{.note-modified}
