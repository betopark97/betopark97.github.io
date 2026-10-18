---
title: dlt
description: Loading data from APIs and other sources into the warehouse with Python.
icon: simple-icons:dlthub
---
This dlt guide / note will be updated to follow the most stable version of the dlt package.
This means that this section does not cover paid services like dltHub or paid features.

Current version: dlt 1.28.2

- [Setup](001-setup.md) — install, marimo dashboard extras
- [Conventions](002-conventions.md) — project layout, configs & secrets, source/pipeline shape, environments
- [Normalization](003-normalization.md) — how JSON becomes tables, and why `max_table_nesting=0`
- [Sources](004-sources.md) — per-provider credential setup
- [Workflow](005-workflow.md) — CLI, drop/refresh modes
- [REST APIs](006-rest-apis.md) — low-level `RESTClient` over declarative `rest_api`, fan-out with transformers
