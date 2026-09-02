---
title: Styling
---
Style rules taken from dbt Labs' [how we style our dbt projects](https://docs.getdbt.com/best-practices/how-we-style/0-how-we-style-our-dbt-projects) guide. These apply to every layer, not just staging. Python model styling is left out since we don't use Python models.

## Model and Field Names

- model names are plural: `customers`, `orders`, `products`. the full file naming grammar is in [Naming](003-naming.md)
- every model has a primary key
- primary key is named `{object}_id`, like `account_id`, so it's obvious which id is referenced downstream
- keys are string data types
- use underscores in model names, never dots
	- most platforms use dots to separate `database.schema.object`, so underscores avoid quoting issues
- same field name across models. a key to `customers` is `customer_id`, not `user_id` or `id`
- no abbreviations or aliases. `customer` not `cust`, `orders` not `o`
- avoid reserved words as column names. the aliasing trick for a source column that is one is in [Staging](006-staging.md)
- booleans prefixed with `is_` or `has_`, and never also suffixed `_flag`. `is_` for state, `has_` for possession: `is_accessed`, `is_ongoing`, `has_golden_hammer`
	- a source `_flag` column keeps the prefix at the front of the whole name, ahead of any `{parent}__{child}` nesting: `boss_contents__complete_flag` becomes `is_boss_contents__completed`
	- the rule assumes the column really is a boolean. how to check and cast is in [Staging](006-staging.md)
- timestamps named `{event}_at` in UTC. non-UTC gets a suffix, like `created_at_pt`
	- our project is KST so we use the `_kst` suffix
- dates named `{event}_date`
- event dates and times in past tense: `created`, `updated`, `deleted`
- price and revenue fields in decimal currency (`19.99` for $19.99). if kept as integer cents, suffix it as `price_in_cents`
- schema, table, and column names in `snake_case`
- names based on business terminology, not source terminology. if the source says `user_id` but the business says customer, use `customer_id`
- model versions use a `_v1`, `_v2` suffix
- consistent ordering of data types, grouped and labeled by type. same order in every layer, not only staging
	- ids -> strings -> numerics -> booleans -> dates -> timestamps

```sql
with

source as (

    select * from {{ source('ecom', 'raw_orders') }}

),

renamed as (

    select

        ----------  ids
        id as order_id,
        store_id as location_id,
        customer as customer_id,

        ---------- strings
        status as order_status,

        ---------- numerics
        (order_total / 100.0)::float as order_total,
        (tax_paid / 100.0)::float as tax_paid,

        ---------- booleans
        is_fulfilled,

        ---------- dates
        date(order_date) as ordered_date,

        ---------- timestamps
        ordered_at

    from source

)

select * from renamed
```

> [!note]
> The `source` + `renamed` shape above is a staging pattern. Intermediate and mart models use `ref()` and joins instead, but the naming and column ordering rules still hold.

## SQL Basics

- no `select *`, with exactly two exceptions
	- the last line of a model, `select * from {final_cte}`
	- a staging import CTE reading off a `{{ source() }}`, as in the example above, because staging is supposed to carry every raw column forward. an import CTE reading off a `{{ ref() }}` never gets this — see [Materializations & Build Time](009-materializations.md)
- all lower case for field names, keywords, and function names
- trailing commas
- four space indents
- lines no longer than 80 characters
- `as` written explicitly when aliasing a field or table
- jinja comments (`{# #}`) for comments that shouldn't end up in the compiled SQL
- [sqlfluff](https://sqlfluff.com/) enforces all of this automatically
	- customize `.sqlfluff` to the project
	- exclude `target/`, `dbt_packages/`, and `macros/` with a `.sqlfluffignore` to speed up linting

## Fields and Aggregations

- fields stated before aggregates and window functions
- aggregate as early as possible, on the smallest data set, before joining
- group and order by number (`group by 1, 2`) instead of listing column names
	- if grouping by more than a few columns, the model design needs another look

## Joins

- prefer `union all` over `union` unless you actually want duplicates removed
- when joining two or more tables, always prefix column names with the table name. single table selects don't need it
- be explicit about the join type. `inner join`, not `join`
- no table aliases in join conditions, especially initialisms. `customers` beats `c`
- always move left to right. a `right join` usually means you should swap which table you select `from` and which you `join` to

## Import CTEs

- all `{{ ref('...') }}` statements go in CTEs at the top of the file
- import CTEs are named after the table they reference
- limit the data scanned. select only the columns used and filter with `where`

```sql
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

## Functional CTEs

- where performance permits, a CTE does a single logical unit of work
- CTE names are as verbose as needed to convey what they do. `events_joined_to_users`, not `user_events`, which is a model name, not a transformation
- CTEs duplicated across models get pulled out into their own intermediate models
- last line of a model is `select * from` the final CTE, so you can swap in an earlier CTE to audit intermediate output while developing

## Model Configuration

- model specific attributes like sort and dist keys go in the model
- configuration that applies to every model in a directory goes in `dbt_project.yml`
- in-model config formatted like this

```sql
{{
    config(
      materialized = 'table',
      sort = 'id',
      dist = 'id'
    )
}}
```

## Example SQL

```sql
with

my_data as (

    select
        field_1,
        field_2,
        field_3,
        cancellation_date,
        expiration_date,
        start_date

    from {{ ref('my_data') }}

),

some_cte as (

    select
        id,
        field_4,
        field_5

    from {{ ref('some_cte') }}

),

some_cte_agg as (

    select
        id,
        sum(field_4) as total_field_4,
        max(field_5) as max_field_5

    from some_cte

    group by 1

),

{# CTE comments go here #}
joined as (

    select
        my_data.field_1,
        my_data.field_2,
        my_data.field_3,

        -- use line breaks to visually separate calculations into blocks
        case
            when my_data.cancellation_date is null
                and my_data.expiration_date is not null
                then expiration_date
            when my_data.cancellation_date is null
                then my_data.start_date + 7
            else my_data.cancellation_date
        end as cancellation_date,

        some_cte_agg.total_field_4,
        some_cte_agg.max_field_5

    from my_data

    left join some_cte_agg
        on my_data.id = some_cte_agg.id

    where my_data.field_1 = 'abc' and
        (
            my_data.field_2 = 'def' or
            my_data.field_2 = 'ghi'
        )

    having count(*) > 1

)

select * from joined
```

## Jinja

- spaces inside delimiters. `{{ this }}`, not `{{this}}`
- newlines to separate logical blocks of jinja
- indent 4 spaces into a jinja block so it's clear the code is wrapped by it
- don't fuss over whitespace control. readable project code beats perfect compiled code

```jinja
{% macro make_cool(uncool_id) %}

    do_cool_thing({{ uncool_id }})

{% endmacro %}
```

```sql
select
    entity_id,
    entity_type,
    {% if this %}

        {{ that }},

    {% else %}

        {{ the_other_thing }},

    {% endif %}
    {{ make_cool('uncool_id') }} as cool_id
```

## YAML

- two space indents
- list items are indented
- a single entry list can be a string like `'select': 'other_user'`, but an explicit list is better: `'select': ['other_user']`
- new line between list items that are dictionaries
- lines no longer than 80 characters
- the [dbt json schema](https://github.com/dbt-labs/dbt-jsonschema) plus prettier validates and formats these automatically

```yaml
models:
  - name: events
    columns:
      - name: event_id
        description: This is a unique identifier for the event
        data_tests:
          - unique
          - not_null

      - name: event_time
        description: "When the event occurred in UTC (eg. 2018-01-01 12:00:00)"
        data_tests:
          - not_null

      - name: user_id
        description: The ID of the user who recorded the event
        data_tests:
          - not_null
          - relationships:
              arguments: # available in v1.10.5 and higher
                to: ref('users')
                field: id
```

## Enforcing Style

- pre-commit hooks catch and often auto-fix violations before the commit lands. [dbt-checkpoint](https://github.com/dbt-checkpoint/dbt-checkpoint) is the dbt specific hook set
	- add this only after the codebase already conforms, otherwise every commit fails
- [dbt_project_evaluator](https://github.com/dbt-labs/dbt-project-evaluator) flags where the project deviates from dbt best practices and recommends fixes. covers modeling, testing, documentation, structure, performance, and governance

***

[Last modified: 2026-09-02]{.note-modified}
