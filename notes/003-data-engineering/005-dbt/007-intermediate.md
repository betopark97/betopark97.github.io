---
title: Intermediate
---
Silver. Where all the transformation happens.

## Allowed

- all transformations
- joins and unions, both intra and inter model
- this is the only layer that encodes business logic before it reaches a mart

## Not Allowed

- reading a source directly. intermediate reads `{{ ref() }}` off staging, never `{{ source() }}`
- final-shape modeling. dim, fct, and bridge tables are [Marts](008-marts.md)

## Naming

`int_{domain}__{entity}.sql`, entity plural. Full grammar in [Naming](003-naming.md).

## Materialization

View by default, table when the model gets heavy. Set under `models.{project}.{domain}.intermediate` in `dbt_project.yml`, see [Project Structure](002-project-structure.md).

## Tests & Contracts

No data contract. This layer is internal, so it stays free to churn. `_int__models.yml` still declares models, columns, data tests, and descriptions.

## Shape

Import CTEs at the top, one `ref()` each, then functional CTEs doing one logical unit of work apiece. A CTE that shows up in more than one model gets pulled out into its own intermediate model. Rules in [Styling](004-styling.md).

***

[Last modified: 2026-10-18]{.note-modified}
