# Materializations & Build Time

How a model gets written to the warehouse, and how to keep the build from getting slow as the project grows.

## The Ladder

You would start with a view (which the build time would be fast), move to table (which the query time would be fast), and later to incremental materializations (which the build time is moderate and the query time would be fast).

| Materialization | Build time | Query time | Use when |
|----|----|----|----|
| view | fast | slow | staging, and intermediate until it hurts |
| table | slow | fast | marts, heavy intermediate models |
| incremental | moderate | fast | the full rebuild stops being worth it |

Defaults per layer are set in `dbt_project.yml`, see [Project Structure](../../../notes/003-data-engineering/004-dbt/002-project-structure.llms.md). Per-model overrides go in the model itself with a `config()` block, see [Styling](../../../notes/003-data-engineering/004-dbt/004-styling.llms.md).

## Incremental Models

Only use `merge`, it’s the only idempotent closes to “set-it-and-forget-it”.\
Remember to add the logic to erase orphaned data.

If the data is too big for `merge`, then use `delete+insert` or `insert_overwrite`.\
`delete+insert` checks for a set of keys that you define.

## Prune Early

The cheapest optimization is not scanning the data in the first place. In an import CTE, select only the columns the model actually uses and push the `where` filter as high as it goes, so every join and transformation below it works on a smaller set.

``` numberSource
with

orders as (

    select
        order_id,
        customer_id,
        order_total,
        order_date

    from {{ ref('orders') }}

    where order_date >= '2020-01-01'

)
```

Staging is the exception. A `select *` off a `{ source() }` is allowed there, because the layer exists to carry every raw column forward — see [Staging](../../../notes/003-data-engineering/004-dbt/006-staging.llms.md). Everywhere else, an import CTE that selects `*` is leaving build time on the table.

## Project-wide Optimizations

The project-wide optimizations would require something like dbt State if you’re willing to go for a freemium or premium subscription.

For the free way to do this would be to chain selectors like `state:modified`, `source_status:fresher`, `config.materialized:view`. Selector syntax is in [Workflow](../../../notes/003-data-engineering/004-dbt/012-workflow.llms.md).

------------------------------------------------------------------------

Last modified: 2026-08-29

Back to top
