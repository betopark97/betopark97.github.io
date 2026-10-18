# Conventions

There is not much to dlt as it’s more like a lightweight tool instead of a framework. That’s why the structure and conventions to setting up dlt is quite free to do as you want. However, there is a `.dlt` folder, which is a dlt-native way to manage dlt configurations.

## Directory Structure

The directory structure will look like the following:

> **NOTE:**
>
> I manage my dependencies with uv hence the pyprojects.yml, uv.lock, and .python-version files.

``` numberSource
dlt_project/
├── .dlt/
│   ├── config.toml                 # non-secret config (log level, runtime, dataset names)
│   ├── secrets.toml                # gitignored — real credentials
│   └── secrets.toml.example        # committed template
│
# >>> custom sources & destinations
├── sources/                        # EXTRACT layer — one package per source
│   ├── __init__.py
│   │
│   ├── {source_a}/
│   │   ├── __init__.py             # @dlt.source + @dlt.resource definitions
│   │   ├── helpers.py              # API client, pagination, auth, retry/backoff
│   │   ├── settings.py             # constants: base URL, endpoints, default params
│   │   └── README.md               # what it pulls, quirks, rate limits
│   │
│   └── {source_b}/
│       ├── __init__.py
│       ├── helpers.py
│       ├── settings.py
│       └── README.md
│
├── destinations/                   # LOAD layer — one package per custom destination
│   ├── __init__.py
│   │
│   ├── {destination_a}/
│   │   ├── __init__.py             # @dlt.destination definitions
│   │   ├── helpers.py              # client, auth, write/flush logic
│   │   └── settings.py             # constants: endpoints, batch size, defaults
│   │
│   └── {destination_b}/
│       ├── __init__.py
│       ├── helpers.py
│       └── settings.py
# <<< custom sources & destinations
│
├── pipelines/                      # LOAD/RUN layer — one runner per pipeline
│   ├── {source_a}_pipeline.py      # dlt.pipeline(...).run({source_a}())
│   └── {source_b}_pipeline.py
│
├── schemas/                        # optional — schema contracts
│   ├── export/                     # dlt writes inferred schemas here
│   └── import/                     # pin/edit schemas here to enforce them
│
├── tests/                          # mirror sources/ structure
│   ├── conftest.py
│   ├── test_{source_a}.py
│   └── test_{source_b}.py
│
├── pyproject.toml                  # deps: dlt[{destination}] + source libs
├── uv.lock
├── .python-version
├── .gitignore                      # ignores .dlt/secrets.toml, .venv, etc.
└── README.md
```

Below will be an explanation of each of the subdirectories and files in logical order. Meaning that this is the order I would fill in the code to run my pipelines.

> **NOTE:**
>
> A good way to build a robust pipeline is to think in enhancing the project in the following order: secrets, idempotency, error/retry handling, incremental optimizations, observability, scheduling, tests, schema drifts. This does not apply only for dlt, but for all data pipelines, too.

### Why a folder per source

The folder-per-source layout is convention-by-example, *not* a hard rule — dlt has no docs page mandating it. It is reverse-engineered from dlt’s own built-in sources (`dlt/sources/*`) and the [verified-sources](https://github.com/dlt-hub/verified-sources) repo. Verified against dlt 1.28.2.

| File | Contains | Nature |
|----|----|----|
| `__init__.py` | the `@dlt.source` function; imports from the others | **wiring** — reads top-to-bottom as intent |
| `settings.py` | static data: `BASE_URL`, endpoint catalog, defaults, constants | **data** — no logic |
| `helpers.py` | pure functions: resource builders, custom paginators/auth, row transforms | **logic** — testable in isolation |

How dlt’s own shipped sources are laid out:

| Source | Files | Notes |
|----|----|----|
| `filesystem` | `__init__.py`, `settings.py`, `helpers.py`, `readers.py` | The full trio + extra. `settings.py` is literally `DEFAULT_CHUNK_SIZE = 100`. `readers.py` holds format-specific read fns. |
| `sql_database` | `__init__.py`, `helpers.py`, `schema_types.py`, `arrow_helpers.py` | **No `settings.py`** — nothing static to hoist. Extra `schema_types.py` for type mapping. |
| `rest_api` | `__init__.py`, `typing.py`, `config_setup.py`, `utils.py` | It’s a *framework*, not a source: `typing.py` = config schema, `config_setup.py` = config→objects. |

So the convention is loose — sources add, skip, and rename files as their needs demand. `settings.py` only appears when there are shared constants. Add a file **when a concern earns one**, not to fill a template; an empty `helpers.py` is fine as a reserved slot.

> **NOTE:**
>
> `dlt init` scaffolds a single-file `*_pipeline.py` quickstart, not this folder layout. The folder pattern comes from the verified-sources repo.

### Scaling: catalog + builder loop

Past a handful of endpoints, stop hand-writing each resource and go data-driven:

| File | Small source | Scaled source |
|----|----|----|
| `settings.py` | flat `ENDPOINTS` (name→path) | enriched catalog (name→`{path, params, write_disposition, primary_key}`) |
| `helpers.py` | (empty) | `build_resource(name, spec)` + any custom paginator/transform |
| `__init__.py` | hand-writes each resource | thin `@dlt.source`; loops the catalog through the builder |

Adding an endpoint then costs one entry in `settings.py` and zero code change. If `__init__.py` imports a builder across the module boundary, make it public (`build_resource`, not `_build_resource`).

## Configs & Secrets

There are various ways to set up configs and secrets. The one I prefer is to use the `.dlt` native features. Then use the dlt supported decorators to call them with `@dlt.source`, `@dlt.resource` and `@dlt.destination`.

> **NOTE:**
>
> Environment variables override `secrets.toml` and `config.toml`. That’s why if you prefer setting up configs and secrets with environment variables you can do so.

### Configs

The configurations are managed by the `config.toml`. This file is to handle non secret variables.

``` numberSource
[runtime]
log_level="INFO"

# Do not compress files sent to the filesystem bucket
[normalize.data_writer]
disable_compression=true

# Recommended sections for the destination (destination.module)
[destination.filesystem]
bucket_url = "s3://[your_bucket_name]"

# Arrow/polars loads skip data-lineage columns by default.
# Turn them on so every row carries 
# _dlt_load_id (joins to _dlt_loads for auditing) and _dlt_id (unique row id).
[normalize.parquet_normalizer]
add_dlt_load_id = true
add_dlt_id = true
```

### Secrets

The secrets are managed by the `secrets.toml`. This file will have the variables for sources and target. The thing is that there is no hard rules to manage these and the following conventions are “one” of the default ways, but also trying to keep it modular.

``` numberSource
[sources.{source_a}]
api_key = "..."

[sources.{source_b}.credentials]
username = "..."
password = "..."

[destination.{destination_a}]
credentials = "db://user:password@service-account/database?warehouse=warehouse_name&role=role"

[destination.{destination_b}.credentials]
host = "..."
username = "..."
password = "..."
database = "..."
```

If the credentials have a predefined format like `SQL database` or `Object store & filesystem`. You can separate by provider name / pipeline name.

``` numberSource
[{provider}.sources.filesystem.credentials]
client_email = "..."
private_key = "..."
project_id = "..."

[{provider}.sources.sql_database.credentials]
drivername = "..."
database = "..."
username = "..."
host = "..."
port = "..."
```

## Pipelines

Normally pipeline files are the starting point. It calls a source and destination through the decorators `@dlt.source` and `@dlt.destination`. However, we wouldn’t make all the mess of using dlt for a project that wouldn’t scale. That’s why I plan to start with a scaffold that I’ve provided above in the directory structure part with the tree.

The pipeline script should look something like the following:

``` numberSource
import dlt

from sources.{source_dir} import {source_dir}


def run() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="{source_dir}",
        destination="{destination}",
        dataset_name="{source_dir}",
    )
    load_info = pipeline.run({source_dir}())
    return load_info
    

if __name__ == "__main__":
    run()
```

## Source

let’s set the `@dlt.source`’s parameter to `max_table_nesting=0` so that it doesn’t do any normalization and we strictly do all transformations in `dbt` the right tool for transformation. we thus use dlt only for what it’s best: extraction and loading (normally dlt works in three steps under the hood: extraction, normalization, and loading).

``` numberSource
@dlt.source(name="{source_name}", max_table_nesting=0)
```

## Variables

Okay, there are a lot of variables to manage, so let’s make a small bullet point list of what values to configure for each of the main variables.

- pipeline_name = the domain or source
- dataset_name = schema
- wrapper = @dlt.source(name={}, section={})
- credentials \[sources.{source}.filesystem.credentials\]

## Environments

To separate environments under `.dlt` make the following configurations:

- `.workspace`: leave it an empty file, it’s to let dlt create its artifacts in this workspace rather than `~/.dlt`.
- `dev.secrets.toml`: exclude variables under `secrets.toml` that belong to dev and add them here.
- `prod.secrets.toml`: exclude variables under `secrets.toml` that belong to prod and add them here.
- `profile-name` (Optional): just add a single text no quotations like: `dev` or `prod` to pin the runs to a specific profile. However, I’d recommend just using `WORKSPACE__PROFILE=prod` when running pipelines to prod instead. All runs default to dev.

### Put the non-secret half in `{profile}.config.toml`

A profile overlay works for `config.toml` too, and that is usually the better\
file. dlt resolves a credential **field by field** across every provider, so a\
credential can be split: the part that identifies an environment goes in\
committed config, and only the actual secret stays in the gitignored file.

``` numberSource
# .dlt/dev.config.toml  -- committed
[destination.postgres.credentials]
database = "dev_maplestory"
```

``` numberSource
# .dlt/secrets.toml  -- gitignored, shared by every profile
[destination.postgres.credentials]
host = "localhost"
port = 5432
username = "..."
password = "..."
```

The point is reviewability: the environment-to-database map is in git and shows\
up in a diff, while nothing secret is. Only fields typed as secrets (`password`,\
API keys) are forced into `secrets.toml`; everything else resolves from config.

### The built-in profiles

`dev` (the default), `prod`, `tests`, and `access`. `dev` and `tests` are\
`LOCAL_PROFILES` — never synced to dltHub. `tests` is worth wiring even before\
there are tests: it exists so a test run cannot touch the data you work\
against, and pointing it at a real database rather than a local duckdb file is\
what lets it catch destination-specific failures.

### State is per profile — this is the real payoff

The workspace moves pipeline state out of `~/.dlt/pipelines/` and into\
`{run_dir}/.dlt/state/{profile}/pipelines/`. Without a workspace, a dev run and\
a prod run of the same `pipeline_name` **share one state directory** and its\
incremental cursors. That, not the config layering, is the reason to reach for\
workspaces rather than swapping `dataset_name` by hand.

Consequence when retrofitting an existing project: the moment `.workspace`\
appears, dlt stops finding the old state. Destination-side state\
(`_dlt_pipeline_state`, `_dlt_loads`, `_dlt_version`) lives in the dataset and\
is re-synced automatically, so this is usually harmless — but copy\
`~/.dlt/pipelines/{name}` into the new location if the pipeline has incremental\
cursors you cannot afford to re-derive.

### Gotchas

- The marker file is the **only** trigger: dlt builds a `WorkspaceRunContext`\
  if and only if `.dlt/.workspace` exists. Its contents are never read.
- Do **not** run `dlthub init` in a directory that already has a `.dlt/`. It\
  scaffolds a workspace and overwrites what is there. `touch .dlt/.workspace`\
  is the whole retrofit.
- `dlt --help` hides the `profile` and `workspace` subcommands until a\
  workspace is initialized, which makes the feature look absent when it is not.
- Commit `.workspace` and every `{profile}.config.toml`; gitignore\
  `.dlt/state/`, `.dlt/data/`, `.dlt/profile-name`, and `.dlt/*.secrets.toml`.

Checking what a profile resolves to, without running a load:

``` numberSource
WORKSPACE__PROFILE=tests python -c "
from dlt.common.configuration.resolve import resolve_configuration
from dlt.destinations.impl.postgres.configuration import PostgresCredentials
print(resolve_configuration(PostgresCredentials(), sections=('destination','postgres')).database)
"
```

### Name the environment in the database, not the dataset

If the destination is Postgres, put the environment in the **database**\
(`dev_maplestory`, `prod_maplestory`) and keep `dataset_name` identical across\
profiles. Prefixing the dataset instead means every downstream source\
definition and query carries the environment as a string.

One naming trap: dlt derives its staging dataset from\
`staging_dataset_name_layout`, default `%s_staging`. A dataset named `nexon`\
produces a schema `nexon_staging`, which collides in meaning with a dbt\
`staging` layer in the same database. Prefix raw datasets — `raw_nexon` gives\
`raw_nexon_staging`, which reads unambiguously.

## Scripts

when running:\
- `WORKSPACE__PROFILE=prod` \# default: dev\
- `INGESTION__{key}={value}` \# e.g., INGESTION\_\_MONTHS_BACK={int\|all} (default: 3)\
- `PROGRESS=log`\
- `PIPELINES__{pipeline_name}__REFRESH={drop_sources|drop_resources|drop_data}`

> **NOTE:**
>
> These environment variables in the config file are for automations (so bots running your pipelines). For humans running scripts, it’s recommended to use cli flags.

------------------------------------------------------------------------

Last modified: 2026-10-18

Back to top
