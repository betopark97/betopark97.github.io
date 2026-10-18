# Node Selection

The selection language that decides *which* nodes a command touches. The commands themselves are in [Workflow](../../../notes/003-data-engineering/005-dbt/012-workflow.llms.md).

“Node” and “resource” mean the same thing here: models, tests, sources, seeds, snapshots, exposures, analyses — everything in the DAG.

## Which Commands Take Selection

| Command | Arguments |
|----|----|
| `run`, `test`, `build` | `--select`, `--exclude`, `--defer` |
| `seed`, `snapshot`, `source freshness`, `docs generate` | `--select`, `--exclude` |
| `ls`, `build` | `--select`, `--exclude`, `--resource-type` |
| `compile` | `--select`, `--exclude`, `--inline` |

## Always Quote the Argument

``` numberSource
dbt build --select "tag:nightly"
```

Unquoted selectors are unreliable across shells and terminals — `*`, `+`, and spaces all get mangled. Quote every time, single argument or not.

## How Selection Resolves

dbt applies the pieces in a fixed order, then filters by resource type:

1.  **Methods** (`tag:`, `path:`, …) match a set of nodes.
2.  **Graph operators** (`+`, `@`) expand each set along the DAG.
3.  **Set operators** (space, comma) combine the expanded sets.
4.  `--exclude` subtracts.
5.  Anything that is not the current task’s resource type is dropped — only models survive `dbt run`, only seeds survive `dbt seed`.

Step 5 is why `dbt run --select "tag:nightly"` silently skips the nightly-tagged seeds. Use `dbt build` when the selection spans resource types.

## Methods

`method:value`. The method is omittable — it defaults to `path`, `file`, or `fqn` — but write it out; an implicit method is a selector nobody can read.

| Method | Selects | Example |
|----|----|----|
| `tag:` | nodes carrying a tag | `"tag:nightly"` |
| `path:` | nodes at or under a directory or file | `"path:models/staging/github"` |
| `file:` | a model by filename, with extension | `"file:stg_issues.sql"` |
| `fqn:` | nodes by fully-qualified name — the `dbt ls` output format | `"fqn:my_project.staging.stg_issues"` |
| `package:` | nodes from a package; `package:this` for the root project | `"package:dbt_utils"` |
| `config.<key>:` | nodes with a matching config | `"config.materialized:incremental"` |
| `resource_type:` | nodes of one type | `"resource_type:source"` |
| `source:` | models downstream of a source, with `+` | `"source:snowplow+"` |
| `exposure:` | parents of an exposure, with `+` | `"+exposure:weekly_kpis"` |
| `test_type:` | `unit`, `data`, `generic`, `singular` | `"test_type:singular"` |
| `test_name:` | instances of one generic test | `"test_name:unique"` |
| `state:` | nodes changed against a comparison manifest | `"state:modified+"` |
| `result:` | nodes by their status in the prior run | `"result:error"` |
| `source_status:` | sources refreshed since the last freshness check | `"source_status:fresher+"` |
| `group:`, `access:`, `version:` | governance properties | `"access:public"` |

`config.` reaches into nested values too — `config.meta.contains_pii:true`, `config.grants.select:reporter`, `config.unique_key:column_a` against a list.

Unix wildcards work in most methods: `*` any run of characters, `?` one character, `[abc]` and `[a-z]` one from the set.

``` numberSource
dbt ls --select "package:*_source"
dbt ls --select "*.marts.*"
```

## Graph Operators

``` numberSource
dbt run --select "+my_model"    # my_model and every ancestor (upstream)
dbt run --select "my_model+"    # my_model and every descendant (downstream)
dbt run --select "+my_model+"   # both directions
```

Quantify the `+` to stop at a given depth:

``` numberSource
dbt run --select "my_model+1"    # first-degree children only
dbt run --select "2+my_model"    # parents and grandparents
dbt run --select "3+my_model+4"  # 3 up, 4 down
```

The `@` operator goes in front only. It selects the model, all its descendants, **and the ancestors of those descendants** — everything needed to actually build the downstream set in an environment where the parents may not exist yet. This is the CI operator.

``` numberSource
dbt build --select "@my_model"
```

## Set Operators

The whitespace-versus-comma distinction is the one that bites.

| Separator | Meaning | Example |
|----|----|----|
| space | **union** — matches *any* argument | `"+stg_orders +stg_customers"` |
| comma, no space | **intersection** — matches *every* argument | `"marts.finance,tag:nightly"` |

``` numberSource
# everything upstream of either model
dbt run --select "+snowplow_sessions +fct_orders"

# only the shared ancestors of both
dbt run --select "+snowplow_sessions,+fct_orders"

# mixed: two intersections, unioned by the space between them
dbt run --select "+snowplow_sessions,+fct_orders marts.finance,tag:nightly"
```

Argument order inside an intersection is irrelevant. A node matched twice appears once.

## Exclude

`--exclude` takes the same syntax as `--select` and subtracts its result.

``` numberSource
dbt run --select "my_package.*+" --exclude "my_package.a_big_model+"
dbt test --exclude "test_name:relationships"
```

## Preview Before Running

`dbt ls` resolves a selector and prints the nodes without executing anything. Use it whenever a selector is more than one term — it is the difference between a wrong CI job and a five-second check.

``` numberSource
dbt ls --select "state:modified+" --state prod-artifacts/
dbt ls --select "source_status:fresher+"
```

## Indirect Test Selection

Selecting a model pulls in its tests too. How aggressively is the `--indirect-selection` flag:

| Mode | Behaviour |
|----|----|
| `eager` (default) | include every test touching a selected node |
| `cautious` | skip tests that also have unselected parents |
| `buildable` | like `cautious`, but keep the test if a selected node is an ancestor |
| `empty` | only tests attached solely to the selected node |

`eager` is right in development. In CI, where half the DAG is deferred to production, `cautious` or `buildable` stops a `relationships` test from running across two environments at once.

## Named Selectors

Once a selector stops fitting on one line, move it to a top-level `selectors.yml` and give it a name.

``` numberSource
selectors:
  - name: nightly_diet_snowplow
    description: Non-incremental Snowplow models that power nightly exports
    definition:
      union:
        - intersection:
            - '@source:snowplow'
            - 'tag:nightly'
        - 'models/export'
        - exclude:
            - intersection:
                - 'package:snowplow'
                - 'config.materialized:incremental'
```

`union:` and `intersection:` are the keyword forms of the space and comma operators. A `definition` can also be a bare CLI-style string (`'tag:nightly'`, operators and all) or a `method: value` pair, which supports no operators at all.

Invoke it with the `--selector` flag:

``` numberSource
dbt run --selector nightly_diet_snowplow
```

A selector marked `default: true` applies to any command run without `--select` or `--exclude`. Only one may be default per invocation.

> **NOTE:**
>
> Passing `--selector` alongside `--select` or `--exclude` makes dbt use `--selector` and silently ignore the others. The `selector:` method — `--select "selector:my_selector tag:nightly"` — that fixes this is v1.12 and later. On v1.11, one or the other.

## State Comparison

`state:` compares the project against a manifest from a previous run, supplied by `--state` or `DBT_ENGINE_STATE`. This is what makes a CI job build only what a pull request changed.

| Selector | Matches |
|----|----|
| `state:new` | no node with this `unique_id` in the comparison manifest |
| `state:modified` | every new node, plus every changed one |
| `state:old` | the node exists in the comparison manifest |
| `state:unmodified` | existing and unchanged |

`state:modified` has subselectors when the full criteria are too broad:

| Subselector | Detects |
|----|----|
| `.body` | model SQL, seed values |
| `.configs` | any node config except `database` / `schema` / `alias` / `tags` / `meta` |
| `.relation` | `database` / `schema` / `alias` — the warehouse representation |
| `.persisted_descriptions` | description changes, only where `persist_docs` is on |
| `.macros` | upstream macro changes, direct or indirect |
| `.contract` | a model contract’s column `name` or `data_type` |

`tags` and `meta` are metadata-only: changing either never triggers `state:modified`, because neither affects materialization. `description` does count, but only with `persist_docs` enabled.

> **NOTE:**
>
> dbt overwrites `target/manifest.json` during parsing, before it reads it for comparison — so the comparison finds nothing, and the error reads as “saved manifest not found”. Copy the production manifest into a separate directory (`prod-artifacts/`, `state/`) and point `--state` there. Never let `--state` and `--target-path` be the same path.

## Defer

`--defer` resolves `ref()` calls against the `--state` manifest instead of the current target, for any node that is both unselected and absent from the database. It lets a handful of end-of-pipeline models build against production parents instead of rebuilding the DAG in a dev schema.

``` numberSource
dbt build --select "state:modified+" --defer --state prod-artifacts/
```

Both `--defer` and `--state` are required. `--favor-state` goes further: prefer the state manifest even when the node *does* exist in the target. Ephemeral models are never deferred — they are pass-throughs for other `ref` calls.

`--defer-state` takes a second manifest, so `state:modified` can compare against one point in time while deferral falls back to another. Unset, it reuses `--state`, which is what you want almost always.

> **NOTE:**
>
> A deferred run reads dev data and production data in the same query. A `relationships` test between a selected model and a deferred parent is comparing across environments — and a dev-only row limit that production does not have will quietly change the result.

## Reusing the Last Run

`result:` reads the prior invocation’s artifacts, so a failed build can be resumed instead of restarted.

``` numberSource
dbt run   --select "result:error" --state target/        # rerun what errored
dbt build --select "1+result:fail" --state target/       # rebuild models behind failed tests
dbt build --select "1+result:fail+" --state target/      # and everything downstream of them
```

`result:fail` is test-only. `result:error` matches any resource that errored. Tests have no descendants, so `result:fail+` on its own returns nothing but the test — the `1+` prefix is what reaches the model.

Pair it with source freshness to run only what new data touched:

``` numberSource
dbt source freshness
dbt build --select "source_status:fresher+" --state prod-artifacts/
```

------------------------------------------------------------------------

Last modified: 2026-10-18

Back to top
