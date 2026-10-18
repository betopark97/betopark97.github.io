# Intermediate

Silver. Where all the transformation happens.

## Allowed

- all transformations
- joins and unions, both intra and inter model
- this is the only layer that encodes business logic before it reaches a mart

## Not Allowed

- reading a source directly. intermediate reads `{ ref() }` off staging, never `{ source() }`
- final-shape modeling. dim, fct, and bridge tables are [Marts](../../../notes/003-data-engineering/005-dbt/008-marts.llms.md)

## Naming

`int_{domain}__{entity}.sql`, entity plural. Full grammar in [Naming](../../../notes/003-data-engineering/005-dbt/003-naming.llms.md).

## Materialization

View by default, table when the model gets heavy. Set under `models.{project}.{domain}.intermediate` in `dbt_project.yml`, see [Project Structure](../../../notes/003-data-engineering/005-dbt/002-project-structure.llms.md).

## Tests & Contracts

No data contract. This layer is internal, so it stays free to churn. `_int__models.yml` still declares models, columns, data tests, and descriptions.

## Shape

Import CTEs at the top, one `ref()` each, then functional CTEs doing one logical unit of work apiece. A CTE that shows up in more than one model gets pulled out into its own intermediate model. Rules in [Styling](../../../notes/003-data-engineering/005-dbt/004-styling.llms.md).

------------------------------------------------------------------------

Last modified: 2026-10-18

Back to top
