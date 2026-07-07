# SCOR DS

## Intro

The Supply Chain Operations Reference (SCOR) Model.

SCOR DS compared to it’s previous state, is not a linear supply chain model anymore but a synchronous network.

## Data Mart Core Architecture

To build a scalable analytical layer, your fact tables should mirror the natural state transitions of an entity (e.g., an order or a batch of product) as it moves through the supply chain.

The data should be prepared using a Conformed Dimension Data Mart approach. This means that your fact tables directly around the 6 execution phases are wrapped tightly by an Orchestration (Log/Audit) dimension to track pipeline health and end-to-end latency.

### 1. Orchestration & Lineage (The Dimension/Audit Layer)

Before analyzing the business, you must analyze the pipeline. This layer tracks data quality, ingestion latencies, and end-to-end processing times.

- **Core Dimension/Fact:** `dim_pipeline_execution`, `fact_data_lineage`
- **Key Columns:** `dag_run_id`, `source_system_status`, `ingestion_timestamp`, `transformation_latency_seconds`, `data_quality_score`
- **Dashboard Visual:** Data pipeline health monitoring, source-to-target latency gauges, rows processed per hour.

### 2. Plan (The Forecasting Mart)

- **Core Fact Table:** `fact_demand_forecast`
- **Grain:** One row per Product_ID per Location_ID per Forecast_Period_Month.
- **Key Columns:** `forecast_quantity`, `historical_actual_quantity`, `capacity_limit_units`, `safety_stock_threshold`
- **Dashboard Visual:** Forecast Accuracy KPI (MAPE), Actual vs. Forecasted Demand trends, Capacity Utilization charts.

### 3. Order (The Digital Transaction Mart)

- **Core Fact Table:** `fact_order_lifecycle`
- **Grain:** One row per Order_Line_Item.
- **Key Columns:** `order_id`, `customer_id`, `order_status_code` (Created, Approved, Invoiced), `order_placement_timestamp`, `gross_amount`, `tax_amount`, `discount_amount`
- **Dashboard Visual:** Daily/Monthly Revenue, Total Orders Placed, Order conversion rates, Average Order Value (AOV).

### 4. Source (The Procurement Mart)

- **Core Fact Table:** `fact_purchase_orders`
- **Grain:** One row per Purchase_Order_Line_Item.
- **Key Columns:** `po_number`, `supplier_id`, `po_creation_timestamp`, `expected_delivery_date`, `actual_received_date`, `ordered_quantity`, `received_quantity`, `unit_cost`
- **Dashboard Visual:** Supplier Lead Time, Supplier OTIF (On-Time In-Full), Procurement spend analysis by vendor.

### 5. Transform (The Manufacturing & Quality Mart)

- **Core Fact Table:** `fact_production_runs`
- **Grain:** One row per Production_Batch_ID or Work_Order_ID.
- **Key Columns:** `work_order_id`, `product_id`, `production_start_timestamp`, `production_end_timestamp`, `total_units_produced`, `defective_units_count`, `machine_downtime_minutes`
- **Dashboard Visual:** First Pass Yield (FPY %), OEE (Overall Equipment Effectiveness), Defect Rate by product line, Production Downtime trends.

### 6. Fulfill (The Logistics & Distribution Mart)

- **Core Fact Table:** `fact_shipment_fulfillment`
- **Grain:** One row per Shipment_ID / Waybill.
- **Key Columns:** `shipment_id`, `order_id`, `warehouse_id`, `carrier_id`, `allocated_timestamp`, `shipped_timestamp`, `delivered_timestamp`, `promised_delivery_date`, `shipping_cost`
- **Dashboard Visual:** Perfect Order Index (POI), Shipping/Last-Mile Cost per order, Warehouse processing time (Click-to-Ship latency).

### 7. Return (The Reverse Logistics Mart)

- **Core Fact Table:** `fact_order_returns`
- **Grain:** One row per Return_Line_Item.
- **Key Columns:** `return_id`, `original_order_id`, `return_request_timestamp`, `return_reason_code`, `disposition_status` (Restocked, Refurbished, Scrapped), `refund_amount`
- **Dashboard Visual:** Return Rate % by product category, Top Reasons for Returns, Financial impact of refunds vs. scrap loss.

### Conformed Dimensions (The “Glue”)

To build an executive dashboard that allows filtering the entire supply chain by a specific product, location, or date, these dimension tables must link seamlessly across all 6 fact tables above:

- `dim_products` — `product_id`, SKU, category, brand, cost_price, retail_price
- `dim_locations` — `location_id`, site_name, type (Warehouse, Plant, Store), region, country
- `dim_date` — `date_id`, calendar_date, day_of_week, month, quarter, year, fiscal_period

### Executive Dashboard Layout Strategy

When setting up your BI tool (Tableau, Power BI, Looker, etc.), structure it into three distinct operational layers:

1.  **The Executive Summary (High Level):** Place 4–5 global KPIs at the very top: Total Revenue (Order), Global OTIF % (Fulfill), Forecast Accuracy (Plan), and Gross Margin %.
2.  **The Supply Chain Funnel (Process Flow):** Build a chronological funnel visualization or linear timeline tracking an order’s lifecycle. Show the average duration (in hours/days) it takes to pass through each phase: `Order Placed → PO Raised → Produced → Shipped → Delivered`.
3.  **The Operational Drill-Downs (Tabbed Views):** Create dedicated tabs for specific team playbooks (e.g., a “Procurement Tab” powered by the Source Mart, a “Plant Operations Tab” powered by the Transform Mart).

------------------------------------------------------------------------

### Quick Reference

#### Process Marts

| \# | Process | Core Table | Grain | Key Columns | Dashboard |
|----|----|----|----|----|----|
| 0 | **Orchestrate** | `dim_pipeline_execution`, `fact_data_lineage` | Per DAG run | `dag_run_id`, `source_system_status`, `ingestion_timestamp`, `transformation_latency_seconds`, `data_quality_score` | Pipeline health, source-to-target latency gauges, rows/hr |
| 1 | **Plan** | `fact_demand_forecast` | Product × Location × Forecast month | `forecast_quantity`, `historical_actual_quantity`, `capacity_limit_units`, `safety_stock_threshold` | Forecast Accuracy (MAPE), Actual vs Forecast, Capacity Utilization |
| 2 | **Order** | `fact_order_lifecycle` (sales) | Order line item | `order_id`, `customer_id`, `order_status_code`, `order_placement_timestamp`, `gross_amount`, `tax_amount`, `discount_amount` | Daily/Monthly Revenue, Total Orders, AOV |
| 3 | **Source** | `fact_purchase_orders` (orders / PO) | PO line item (PO Number x Product) | `po_number`, `product_id`, `supplier_id`, `po_creation_timestamp`, `expected_delivery_date`, `actual_received_date`, `ordered_quantity`, `received_quantity`, `unit_cost` | Supplier Lead Time, OTIF, Spend by vendor |
| 4 | **Transform** | `fact_production_runs` | Production batch / Work order | `work_order_id`, `product_id`, `production_start_timestamp`, `production_end_timestamp`, `total_units_produced`, `defective_units_count`, `machine_downtime_minutes` | First Pass Yield %, OEE, Defect Rate, Downtime trends |
| 5-a | **Fulfill** | `fact_shipment_fulfillment` | Shipment / Waybill | `shipment_id`, `order_id`, `warehouse_id`, `carrier_id`, `allocated_timestamp`, `shipped_timestamp`, `delivered_timestamp`, `promised_delivery_date`, `shipping_cost` | Perfect Order Index, Cost/order, Click-to-Ship latency |
| 5-b | **Fulfill** | `fact_warehouse_inventory_snapshot` | Warehouse x SKU x Day | `snapshot_date`, `warehouse_id`, `product_id`, `ending_on_hand_quantity`, `daily_allocated_overhead_cost` | Inventory Turnover Ratio, Days Sales of Inventory (DSI), Total Warehousing Carrying Cost |
| 6 | **Return** | `fact_order_returns` | Return line item | `return_id`, `original_order_id`, `return_request_timestamp`, `return_reason_code`, `disposition_status`, `refund_amount` | Return Rate %, Top reasons, Refund vs Scrap impact |

#### Conformed Dimensions

| Dimension | Key Columns | Description / SCM Context |
|----|----|----|
| `dim_products` | `product_id`, SKU, category, brand, cost_price, retail_price | Master catalog for items. Updated with weight/material columns to calculate sustainability metrics (EV.1.1). |
| `dim_locations` | `location_id`, site_name, type (Warehouse/Plant/Store), region, country | The geographical backbone. Shared by fulfillment warehouses, production plants, and customer shipping zones. |
| `dim_date` | `date_id`, calendar_date, day_of_week, month, quarter, year, fiscal_period | The universal calendar heartbeat used to calculate cycle times, monthly revenue, and daily inventory snapshots. |
| `dim_supplier_profile` | `supplier_id`, supplier_name, tier_ranking, risk_score, compliance_status, country | The master record for vendors. Used by fact_purchase_orders to slice spend and track supplier network risk. |
| `dim_bill_of_materials` | `parent_sku`, `component_sku`, required_quantity, effectivity_start_date, effectivity_end_date | The structural map of your products. Allows you to break down a finished item into its raw component parts. |

## Metrics

> **NOTE:**
>
> Three overarching focus areas, spread across 8 performance attributes.

> **WARNING:**
>
> These are not all the metrics. These top metric are the level 1 metrics, but they can funnel down until level 3 metrics (so start with top metrics and dive as you get mature).

### 1. Resilience Focus (Customer-Facing)

- Reliability (RL): Measures process predictability and execution quality.
  - Top Metric: Perfect Order Fulfillment (RL.1.1)
- Responsiveness (RS): Measures operational execution speed and cycle times.
  - Top Metric: Order Fulfillment Cycle Time (RS.1.1)
- Agility (AG): Measures system adaptability and capacity to handle unexpected external shifts or disruptions.
  - Top Metric: Supply Chain Agility (AG.1.1)

### 2. Economic Focus (Internal Business)

- Costs (CO): Measures total operational expenditures incurred across the pipeline.
  - Top Metric: Total Supply Chain Management Costs (CO.1.1)
- Profit (PR): Measures the direct bottom-line financial outcome generated by the supply chain.
  - Top Metric: Earnings Before Interest and Taxes (EBIT) as a Percent of Revenue (PR.1.1)
- Asset Management Efficiency (AM): Measures capital utilization and asset turn speeds.
  - Top Metric: Cash-to-Cash Cycle Time (AM.1.1)

### 3. Sustainability Focus (Outward Impact)

- Environmental (EV): Measures resource footprints, waste generation, and green performance.
  - Top Metric: Materials Used / Total Footprint (EV.1.1)
- Social (SC): Measures corporate responsibility, labor compliance, and governance safety protocols.
  - Top Metric: Diversity and Inclusion / Policy Compliance Score (SC.1.1)

------------------------------------------------------------------------

Last modified: 2026-06-16

Back to top
