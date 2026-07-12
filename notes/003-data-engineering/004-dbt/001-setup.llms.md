# Setup

## Installation: dbt Fusion

> **NOTE:**
>
> We are sticking with the stable dbt core for now because dbt Fusion is still under active development and causes compatibility issues with our current workflows.

``` numberSource
# Curl install
curl -fsSL https://public.cdn.getdbt.com/fs/install/install.sh | sh -s -- --update

# Brew install
brew install dbt
```

## Installation: dbt core

``` numberSource
# Pyproject.toml
uv add dbt-core

# Provider (of choice)
uv add dbt-snowflake dbt-postgres
```

## Check installation

``` numberSource
dbt --version

dbt init --skip-profile-setup
```

## Useful dbt-packages

1.  [dbt-labs/dbt_utils](https://hub.getdbt.com/dbt-labs/dbt_utils/latest/)
2.  [godatadriven/dbt_date](https://hub.getdbt.com/godatadriven/dbt_date/latest/)
3.  [Snowflake-Labs/dbt_semantic_view](https://hub.getdbt.com/Snowflake-Labs/dbt_semantic_view/latest/)

## Useful dbt related python packages

1.  dbt-{database adapter} (e.g., dbt-postgres, dbt-snowflake)
    - adds support for a specific database.
2.  dbt-autofix
    - official command-line utility designed to automate the refactoring and updating of dbt projects.
3.  dbt-osmosis
    - streamlines the management of YAML files by ensuring consistency and accuracy in dbt docs and the actual models.
4.  dbterd
    - detects entity relationships through test relationships, semantic entities, and model contract constraints to make an ERD.
5.  dbt-state (Coming soon…; On afterthought it seems like it’s a freemium feature…)
    - saves compute costs and development time by avoiding unnecessary model builds by comparing current definitions against past runs to skip execution if nothing has changed or cloning existing nodes.

------------------------------------------------------------------------

Last modified: 2026-07-08

Back to top
