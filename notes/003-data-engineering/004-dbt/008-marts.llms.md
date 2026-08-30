# Marts

Gold. Star or snowflake schema, modeled for the business rather than for the pipeline.

## Allowed

- dimension, fact, and bridge tables
- BI and semantic models, materialized as views on top of the tables
- joins and unions, both intra and inter model

## Not Allowed

- staging-grade cleanup. anything that is a rename or a cast should have happened three layers ago
- one-off reporting logic that only a single dashboard needs

The mart table types, and when to reach for each, are covered in [Types of Mart Tables](../../../notes/003-data-engineering/001-data-modeling/002-types-of-mart-tables.llms.md).

## Naming

`{dim|fct|bridge}_{domain}__{entity}.sql`, entity plural. There is no `marts_` prefix — the layer is expressed by which of the three the model is. Full grammar in [Naming](../../../notes/003-data-engineering/004-dbt/003-naming.llms.md).

## Materialization

Table, moving to incremental once the build time justifies it. BI and semantic models stay views. Set under `models.{project}.{domain}.marts` in `dbt_project.yml`, see [Project Structure](../../../notes/003-data-engineering/004-dbt/002-project-structure.llms.md). The ladder and the incremental strategies are in [Materializations & Build Time](../../../notes/003-data-engineering/004-dbt/009-materializations.llms.md).

## Tests & Contracts

- a data contract applies to this layer
- `_marts__models.yaml` declares models, columns, data tests, and descriptions
- `+grants` is set per mart so the right roles can read it, see [Documentation](../../../notes/003-data-engineering/004-dbt/011-documentation.llms.md)
- conservation tests live here in practice, since this is where a wrong row count actually costs something. See [Tests](../../../notes/003-data-engineering/004-dbt/010-tests.llms.md)

------------------------------------------------------------------------

Last modified: 2026-08-29

Back to top
