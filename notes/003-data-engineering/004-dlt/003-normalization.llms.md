# Normalization

dlt normalizes API responses by default. **Two rules:**

1.  **Nested object (dict) → flattened columns**, joined with `__`.
2.  **Nested list (array) → a separate child table**, linked back to its parent.

## Input

Say a resource named `foo` yields this one record:

``` numberSource
{
  "id": 1,
  "name": "alpha",
  "bar": { "x": 10, "y": { "z": 99 } },
  "baz": ["p", "q"],
  "qux": [
    { "k": "a", "n": 1 },
    { "k": "b", "n": 2 }
  ]
}
```

`bar` is an object, `baz` is a list of scalars, `qux` is a list of objects.

## Output tables (default normalization)

### Root table: `foo`

| id  | name  | bar\_\_x | bar\_\_y\_\_z | \_dlt_id | \_dlt_load_id |
|-----|-------|----------|---------------|----------|---------------|
| 1   | alpha | 10       | 99            | `a1b2…`  | `17840…`      |

- `id`, `name` — top-level scalars stay as columns.
- `bar__x`, `bar__y__z` — the object `bar` (and the deeper object `y`) are **flattened** into columns. Each `__` = one object level.
- `baz` and `qux` are **not** here — they’re lists, so they became their own tables.

### Child table: `foo__baz` (list of scalars)

| value | \_dlt_id | \_dlt_parent_id | \_dlt_list_idx |
|-------|----------|-----------------|----------------|
| p     | `c3…`    | `a1b2…`         | 0              |
| q     | `c4…`    | `a1b2…`         | 1              |

A list of plain values becomes a table with a single `value` column, one row per element.

### Child table: `foo__qux` (list of objects)

| k   | n   | \_dlt_id | \_dlt_parent_id | \_dlt_list_idx |
|-----|-----|----------|-----------------|----------------|
| a   | 1   | `d5…`    | `a1b2…`         | 0              |
| b   | 2   | `d6…`    | `a1b2…`         | 1              |

Each object in the list becomes a row; its keys become columns.

## The linking columns dlt adds

| column           | appears in   | meaning                                      |
|------------------|--------------|----------------------------------------------|
| `_dlt_id`        | every table  | unique id for that row                       |
| `_dlt_parent_id` | child tables | the parent row’s `_dlt_id` — the join key    |
| `_dlt_list_idx`  | child tables | the element’s position in the original array |
| `_dlt_load_id`   | root table   | which load run produced the row              |

Every child’s `_dlt_parent_id` equals the root row’s `_dlt_id`. That’s the parent→child link.

``` numberSource
-- root + its qux list items
select f.id, f.name, q.k, q.n, q._dlt_list_idx
from foo f
join foo__qux q on q._dlt_parent_id = f._dlt_id
order by f.id, q._dlt_list_idx;
```

## Deeper nesting

The pattern recurses. A list inside `qux` (e.g. `qux[].items`) creates `foo__qux__items`, whose `_dlt_parent_id` points at the `foo__qux` row. Each extra `__<name>` on a **table** = one more level of **list** nesting.

## Name handling

dlt sanitizes names to be SQL-safe: lowercased, camelCase/spaces/hyphens → `snake_case` (`itemEquipment` → `item_equipment`). Set resource `name` explicitly so table names are predictable rather than derived.

## `max_table_nesting = 0` — the default I use

The same input produces **one** table, no children — every nested object *and* list is stored as a single `jsonb` column:

| id | name | bar | baz | qux | \_dlt_id | \_dlt_load_id |
|----|----|----|----|----|----|----|
| 1 | alpha | `{"x":10,"y":{"z":99}}` | `["p","q"]` | `[{"k":"a","n":1},…]` | `a1b2…` | `17840…` |

Top-level scalars stay columns; `bar`/`baz`/`qux` are left as raw `jsonb`, unnested downstream in dbt with `->`, `->>`, `jsonb_array_elements`. See [Source](../../../notes/003-data-engineering/004-dlt/002-conventions.llms.md#source) for why — dlt does extraction and loading, dbt does transformation.

`max_table_nesting` controls *storage*. `data_selector` and transformer fan-out control *extraction* — what records flow through in memory. They are independent; see [REST APIs](../../../notes/003-data-engineering/004-dlt/006-rest-apis.llms.md).

------------------------------------------------------------------------

Last modified: 2026-10-18

Back to top
