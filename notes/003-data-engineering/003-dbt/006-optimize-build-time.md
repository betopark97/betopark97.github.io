---
title: Optimize Build Time
---
## Project-wide Optimizations

The project-wide optimizations would require something like dbt State if you're willing to go for a freemium or premium subscription.

For the free way to do this would be to chain selectors like `state:modified`, `source_status:fresher`, `config.materialized:view`

## Model-wide Optimizations

You would start with a view (which the build time would be fast), move to table (which the query time would be fast), and later to incremental materializations (which the build time is moderate and the query time would be fast).

***

[Last modified: 2026-06-26]{.note-modified}
