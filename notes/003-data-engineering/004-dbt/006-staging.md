---
title: Staging
---
Bronze. Maps the raw source onto standard business entities so that nothing downstream has to think about how the source happened to shape its data.

## Allowed

- rename columns
- type cast columns
- basic computations, mostly for conversions or type casting
- categorizing (enums, booleans)
- variant / semi-structured normalization
- map source table names to standard business entities
- joins and unions **within the same source**, which normalizing variant columns sometimes needs

## Not Allowed

- business logic of any kind, that is [Intermediate](007-intermediate.md)'s job
- joins or unions across sources
- dropping source detail. staging keeps every single detail and data from the raw source

## Naming

`stg_{source}__{entity}.sql`, entity plural. The domain slot holds the **source**, not the domain — this is the one layer where that is true. Full grammar in [Naming](003-naming.md).

## Materialization

View. Set project-wide under `models.{project}.{domain}.staging` in `dbt_project.yml`, see [Project Structure](002-project-structure.md).

## Column Order

Group and label columns by data type:

```
ids -> strings -> numerics -> booleans -> dates -> timestamps
```

This ordering holds in every layer, not just staging. The worked example is in [Styling](004-styling.md).

## Tests & Contracts

- a data contract applies to this layer
- `_stg__sources.yaml` declares the source database and schema plus a brief documentation of the origin of the data
- `_stg__models.yaml` declares models, columns, data tests, and descriptions

## Shape

The `source` + `renamed` two-CTE pattern, written out in full in [Styling](004-styling.md). Staging is the only place where `select *` off a `{{ source() }}` is allowed, because the layer is supposed to see every raw column — see [Materializations & Build Time](009-materializations.md) for why every other import CTE prunes instead.

***

[Last modified: 2026-08-29]{.note-modified}
