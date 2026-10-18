---
title: Layers
---
We follow Kimball's three layered data warehouse: staging, intermediate, marts. The medallion names for the same three are bronze, silver, gold. The modeling theory behind this sits in the [Data Modeling](../002-data-modeling/index.md) section — this page is only about how the layers land in dbt.

Each layer gets its own page. Read the matrix first, then the page for the layer you are writing in.

| | [Staging](006-staging.md) | [Intermediate](007-intermediate.md) | [Marts](008-marts.md) |
| --- | --- | --- | --- |
| Medallion | bronze | silver | gold |
| Node color | `#CD7F32` | `#A0A0A0` | `#FFD700` |
| Purpose | make the raw source usable | apply business logic | serve the business |
| Joins / unions | intra-source only | intra and inter model | intra and inter model |
| Business logic | no | yes | yes |
| Materialization | view | view, table when heavy | table, incremental when big |
| Database | `{STAGE_DB}` | `{STAGE_DB}` | `{MART_DB}` |
| Data contract | yes | no | yes |
| Naming | `stg_{source}__{entity}` | `int_{domain}__{entity}` | `{dim\|fct\|bridge}_{domain}__{entity}` |
| Meta files | `_stg__sources.yml`, `_stg__models.yml` | `_int__models.yml` | `_marts__models.yml` |

## Where the Line Is

The layer descriptions can read as confusing because staging also transforms. The difference is **business logic**. Staging casts, renames, and normalizes so the data is usable, and keeps every single detail and data from the raw source while doing it. The moment a transformation encodes a business decision, it belongs in intermediate.

Contracts sit on the two boundaries that other people depend on: staging, because everything downstream reads it, and marts, because the business reads it. Intermediate is ours to churn, so it carries no contract. The contract format is in [Documentation](011-documentation.md).

***

[Last modified: 2026-10-18]{.note-modified}
