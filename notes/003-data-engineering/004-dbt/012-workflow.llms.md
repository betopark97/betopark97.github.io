# Workflow

## Commands

| Command | What it does |
|----|----|
| `dbt debug` | validates the connection, profile, and project config |
| `dbt clean` | deletes everything in `clean-targets` (`target/`, `dbt_packages/`) |
| `dbt deps` | installs the packages pinned in `packages.yml` |
| `dbt run` | materializes models |
| `dbt test` | runs data tests |
| `dbt build` | `run` + `test` + `seed` + `snapshot` in dependency order, per node |
| `dbt seed` | loads the CSVs in `seeds/` |
| `dbt docs generate` | builds the catalog, see [Documentation](../../../notes/003-data-engineering/004-dbt/011-documentation.llms.md) |

`dbt build` is the one to reach for by default. It interleaves tests with runs node by node, so a failing test stops the downstream models instead of letting them build on bad data.

## Linting and Formatting

dbt Core has no lint or format command. [sqlfluff](https://sqlfluff.com/) does both, invoked directly:

``` numberSource
sqlfluff lint models/
sqlfluff fix models/
```

The rules it enforces and the `.sqlfluff` / `.sqlfluffignore` setup live in [Styling](../../../notes/003-data-engineering/004-dbt/004-styling.llms.md).

> **NOTE:**
>
> `dbt lint` (requires `.sqlfluff`) and `dbt fmt` are dbt Fusion commands. We are on Core, so neither exists here. Worth revisiting if Fusion ever becomes the main engine — see the Fusion note in [Setup](../../../notes/003-data-engineering/004-dbt/001-setup.llms.md).

## Flags

``` numberSource
-t | --target      # which profiles.yml output to run against
-s | --select      # which nodes to run
-x | --fail-fast   # stop on the first failure
```

## Graph Operators

``` numberSource
+model    # the model and everything upstream of it
model+    # the model and everything downstream of it
+model+   # both directions
```

Selectors compose, which is what makes the build-time optimizations in [Materializations & Build Time](../../../notes/003-data-engineering/004-dbt/009-materializations.llms.md) possible.

------------------------------------------------------------------------

Last modified: 2026-08-29

Back to top
