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

## Renaming a Reserved Word

When the source column is a reserved word, alias it **once, in the import CTE**, rather than at each point of use:

```sql
with character_ability as (

    select
        *,
        date as snapshot_date

    from {{ source('nexon', 'character_ability') }}

),
```

The import CTE then carries both names, so every downstream reference works unchanged — bare, table-qualified, and `using (snapshot_date, ocid)` alike. Aliasing at the point of use instead means deciding, CTE by CTE, whether this one reads the raw import (needs `date as snapshot_date`) or an already-renamed CTE (needs plain `snapshot_date`), and getting it wrong in one branch of a `union all` breaks the build. The duplicate lives inside the import CTE only: every other CTE selects explicit columns, so the model output carries just the new name.

Only staging can do this, because only staging's import CTE is allowed `select *`.

## Casting Source Booleans

Check the value domain before you cast. A column named `*_flag` is not necessarily a boolean:

```sql
select col, count(*) from {{ source(...) }} group by 1;
```

Postgres accepts `0`, `1`, `true`, and `false` from text, so those cast straight with `::boolean`. Localized labels do not — a Korean API happily returns `미적용` / `미사용` / `가능` / `비인간형` in a field whose name ends in `_flag`. Those need a `case`.

When only one of the two values appears in the data you have, do not guess the counterpart string:

```sql
case
    when x is null then null
    when x = '미적용' then false
    else true
end as has_golden_hammer
```

This stays correct whatever the unseen value turns out to be, as long as the field is two-valued. Mapping the observed value and leaving `else null` silently nulls out every row of the other kind instead.

Check for empty strings too. `''::boolean` errors where `null::boolean` is fine, so confirm the blanks are real NULLs before a cast reaches production data.

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
- `_stg__sources.yml` declares the source database and schema plus a brief documentation of the origin of the data
- `_stg__models.yml` declares models, columns, data tests, and descriptions

## Shape

The `source` + `renamed` two-CTE pattern, written out in full in [Styling](004-styling.md). Staging is the only place where `select *` off a `{{ source() }}` is allowed, because the layer is supposed to see every raw column — see [Materializations & Build Time](009-materializations.md) for why every other import CTE prunes instead.

***

[Last modified: 2026-09-02]{.note-modified}
