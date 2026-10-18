---
title: Prefect
description: Orchestrating and monitoring Python data pipelines.
icon: simple-icons:prefect
---
Why use Prefect? and best practices.

### 1. Key Components of Data Pipeline Monitoring

* **Instrumentation:** Generating logs to capture errors and emitting metrics to measure performance.
* **Collection & Storage:** Aggregating logs and metrics from various sources (using agents, log trawling, or APIs like OpenTelemetry).
* **Observability:** Centralizing data into a dashboard to track trends, inspect logs, and identify root causes quickly.
* **Alerting & Remediation:** Setting metric thresholds that trigger manual notifications (e.g., to on-call staff) or automated fixes (e.g., auto-scaling clusters).

---

### 2. Best Practices

* **Avoid Monolithic Architecture:** Modularize your pipeline into separate components (ingestion, transformation, storage, reporting). Monitoring each part independently isolates failures and prevents cascading errors.
* **Make Dependencies Explicit:** Define and document precise inputs/outputs for each step. Use tools like Pydantic to validate data types before processing to catch errors early with clear messages.
* **Define Clear Metrics & Thresholds:**
* **Consistency:** Track completion success rates and allowable downtime between successful runs.
* **Timeliness:** Monitor pipeline duration and latency to detect unusual slowdowns or premature stops.
* **Validity:** Classify error types (e.g., expected API downtime vs. unexpected malformed data).


* **Centralize Logging and Alerting:** Ship all logs and metrics to a single platform and tag runs (e.g., with UUIDs) to trace requests across multi-cloud or hybrid environments.
* **Use Reliable Monitoring Infrastructure:** Avoid building complex custom monitoring tools that create additional single points of failure; leverage dedicated workflow orchestration platforms (like Prefect) instead.