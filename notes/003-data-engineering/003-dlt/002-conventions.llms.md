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

------------------------------------------------------------------------

Last modified: 2026-07-12

Back to top
