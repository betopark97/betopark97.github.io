# Workflow

Which command to run, how to shape it, and where a flag is allowed to live. Which *nodes* the command touches is [Node Selection](../../../notes/003-data-engineering/005-dbt/013-node-selection.llms.md).

## Command Shape

``` numberSource
dbt <subcommand> [flags]
```

Flags go **after** the subcommand. Putting them before it (`dbt --fail-fast run`) is legacy behaviour dbt Labs can drop at any release, and the same flag on both sides is unsupported.

| Flag kind | Shape | Example |
|----|----|----|
| boolean | `--<config>` / `--no-<config>` | `dbt run --fail-fast`, `dbt run --no-fail-fast` |
| non-boolean | `--<config>=<setting>` | `dbt test --indirect-selection=cautious` |

## Commands

| Command | What it does |
|----|----|
| `dbt debug` | validates the connection, profile, and project config |
| `dbt clean` | deletes everything in `clean-targets` (`target/`, `dbt_packages/`) |
| `dbt deps` | installs the packages pinned in `packages.yml` |
| `dbt seed` | loads the CSVs in `seeds/` |
| `dbt run` | materializes **models only** — no tests, seeds, or snapshots |
| `dbt test` | runs data tests and unit tests |
| `dbt snapshot` | runs snapshots |
| `dbt build` | `seed` + `run` + `test` + `snapshot` in dependency order, per node |
| `dbt compile` | renders jinja to `target/compiled/`, runs nothing |
| `dbt ls` | prints the nodes a selector resolves to, runs nothing |
| `dbt source freshness` | checks source `loaded_at` and writes `sources.json` |
| `dbt docs generate` | builds the catalog, see [Documentation](../../../notes/003-data-engineering/005-dbt/011-documentation.llms.md) |

`dbt build` is the default reach. It interleaves tests with runs node by node, so a failing test stops the downstream models instead of letting them build on bad data.

## Flags

Ordered by how often I actually reach for them.

| Flag | Short | What it does |
|----|----|----|
| `--target` | `-t` | which `profiles.yml` output to run against |
| `--select` | `-s` | which nodes to run — see [Node Selection](../../../notes/003-data-engineering/005-dbt/013-node-selection.llms.md) |
| `--exclude` |  | remove nodes from the `--select` set |
| `--fail-fast` | `-x` | stop on the first failure instead of finishing the run |
| `--full-refresh` | `-f` | rebuild incremental models from scratch as tables |
| `--empty` |  | schema-only dry run: refs and sources limited to zero rows |
| `--state` |  | path to a comparison manifest, for `state:` and `--defer` |
| `--defer` |  | resolve unbuilt refs against `--state` instead of the target |
| `--store-failures` |  | write failing test rows to a table instead of discarding them |
| `--warn-error` |  | treat every warning as an error |
| `--threads` |  | override the thread count from `profiles.yml` |

### `--full-refresh`

Reach for it when an incremental model’s schema changed, or when its logic changed and the existing rows are now wrong. It makes `is_incremental()` return `false` for **every** model in the invocation, so scope it with `--select`:

``` numberSource
dbt run --select "fct_orders" --full-refresh
```

Incremental strategy itself is in [Materializations & Build Time](../../../notes/003-data-engineering/005-dbt/009-materializations.llms.md).

### `--empty`

Executes the model SQL against the warehouse with zero-row inputs. Validates that the DAG compiles and the models build, without paying for the scan. This is the cheap pre-flight before a full run.

``` numberSource
dbt build --empty --select "state:modified+" --state prod-artifacts/
```

## Where a Flag Lives

Same flag, four possible homes. Most specific wins:

``` numberSource
CLI option  >  environment variable  >  dbt_project.yml flags:  >  ~/.dbt/user_settings.yml  >  dbt default
```

| Home | Use it for |
|----|----|
| CLI option | behaviour specific to *this invocation* |
| environment variable | behaviour that differs per environment — dev, prod, CI |
| `flags:` in `dbt_project.yml` | version-controlled defaults for everyone on the project |
| `~/.dbt/user_settings.yml` | personal preference across every project on this machine |

``` numberSource
# dbt_project.yml
flags:
  fail_fast: true
```

``` numberSource
export DBT_ENGINE_FAIL_FAST=1   # env var
dbt run --no-fail-fast          # CLI wins over both
```

> **NOTE:**
>
> v1.11 and later use `DBT_ENGINE_`. v1.10 and earlier used plain `DBT_`. Anything copied off an older blog post or an old CI file is setting a variable dbt no longer reads, silently.

Two exceptions to the four homes:

- **Path flags** (`--state`, `--log-path`, `--target-path`) cannot go in `dbt_project.yml`. CLI or env var (`DBT_ENGINE_STATE`, `DBT_ENGINE_LOG_PATH`) only. Path configs that tell dbt where *project resources* live — `model-paths`, `seed-paths` — are different: they are static top-level keys in `dbt_project.yml`, outside the `flags:` dict.
- **Behaviour-change opt-ins** can *only* go in `dbt_project.yml`, so the migration is reviewed in a pull request rather than diverging per machine.

Jinja can read a flag through the `flags` context variable, upper-cased:

``` numberSource
# dbt_project.yml
on-run-start:
  - '{{ log("stopping at the first failure", info = true) if flags.FAIL_FAST }}'
```

## Linting and Formatting

dbt Core has no lint or format command. [sqlfluff](https://sqlfluff.com/) does both, invoked directly:

``` numberSource
sqlfluff lint models/
sqlfluff fix models/
```

The rules it enforces and the `.sqlfluff` / `.sqlfluffignore` setup live in [Styling](../../../notes/003-data-engineering/005-dbt/004-styling.llms.md).

> **NOTE:**
>
> `dbt lint` (requires `.sqlfluff`) and `dbt fmt` are dbt Fusion commands. We are on Core, so neither exists here. Worth revisiting if Fusion ever becomes the main engine — see the Fusion note in [Setup](../../../notes/003-data-engineering/005-dbt/001-setup.llms.md).

------------------------------------------------------------------------

Last modified: 2026-10-18

Back to top
