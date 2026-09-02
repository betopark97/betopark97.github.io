---
title: Project Structure
---
This page covers the shape of the project on disk and the three meta files that configure it. Naming rules for the files inside `models/` live in [Naming](003-naming.md).

## Project Directory Structure

Let's first get a grasp of the bigger picture by looking at how the full directory structure looks like:

```text
dbt_project/
├── .dbt/                              # Profiles dir (optional, project-local)
│   └── profiles.yml                   # Connection profiles (git-ignored)
├── analyses/                          # Ad-hoc analytical queries (not materialized)
├── dbt_packages/                      # Installed packages (git-ignored)
├── logs/                              # Run logs (git-ignored)
├── macros/                            # Custom macros & generic tests
│   └── generate_schema_name.sql
├── models/
│   └── {domain}/
│       ├── staging/
│       │   ├── _stg__sources.yml     # Source db/schema + origin docs
│       │   ├── _stg__models.yml      # Models, columns, tests, descriptions
│       │   └── stg_{source}__{entity}.sql
│       ├── intermediate/
│       │   ├── _int__models.yml
│       │   └── int_{domain}__{entity}.sql
│       └── marts/
│           ├── _marts__models.yml
│           └── {dim|fct|bridge}_{domain}__{entity}.sql
├── seeds/                             # Static CSV reference data
├── snapshots/                         # SCD type-2 snapshots
├── target/                            # Compiled SQL & artifacts (git-ignored)
├── tests/                             # Singular (complex) data tests
│   └── assert_{domain}__{condition}.sql
├── .env                               # Env vars (git-ignored, see the warning below)
├── .gitignore
├── dbt_project.yml                    # Project config
└── packages.yml                       # Package dependencies
```

Below we'll discuss what each component is and how to fill them in.

> [!note] 
> If there is only one domain, there is no need to nest the staging, intermediate, and marts layer. Just simply go with `models/{staging|intermediate|marts}`.

## Project Level Meta Files

### dbt_project.yml

```yaml
name: '{project_name}'
version: '{version}'
config-version: 2

profile: '{project_name}'

model-paths: ['models']
analysis-paths: ['analyses']
test-paths: ['tests']
seed-paths: ['seeds']
macro-paths: ['macros']
snapshot-paths: ['snapshots']

target-path: "target"
clean-targets:
  - 'target'
  - 'dbt_packages'

models:
  +persist_docs:
    relation: true
    columns: true
  {project_name}:
    {domain}: # repeat this block per domain (optional)
      +schema: {SCHEMA}
      +grants: # domain-level default grants (optional)
        {privilege}: ['{ROLE}'] # e.g. select, references
      staging:
        +materialized: view
        +database: {STAGE_DB}
        +docs:
          node_color: "#CD7F32" # bronze color
      intermediate:
        +materialized: view # or table when heavy
        +database: {STAGE_DB}
        +docs:
          node_color: "#A0A0A0" # silver color
      marts:
        +materialized: table
        +database: {MART_DB}
        +docs:
          node_color: "#FFD700" # gold color
        +grants: # optional: override domain grants for marts
          {privilege}: ['{ROLE}', '{ROLE}'] # e.g. select, references
        +tags: ['{tag}'] # optional

seeds:
  {project_name}:
    +database: {STAGE_DB}
    {domain}: # repeat this block per domain
      +schema: {SCHEMA}
      +quote_columns: true # optional
      +docs:
        node_color: "#008000" # green color
      +grants: # optional
        {privilege}: ['{ROLE}'] # e.g. select, references
```

### packages.yml

```yaml
packages:
	- package: dbt-labs/dbt_utils
	  version: 1.3.2
	- package: godatadriven/dbt_date
	  version: 0.17.0
	- package: Snowflake-Labs/dbt_semantic_view
	  version: 1.0.3
```

### profiles.yml

~~~~tabs

tab: Postgres

```yaml
{project_name}:
  target: dev
  outputs:
    dev:
      type: {adapter_type}
      host: "{{ env_var('host') }}"
      user: "{{ env_var('user') }}"
      password: "{{ env_var('password') }}"
      port: "{{ env_var('port') }}"
      database: DEV_STAGE
      schema: {public} # default, macro will manage this
      threads: 16
    test:
      type: {adapter_type}
      host: "{{ env_var('host') }}"
      user: "{{ env_var('user') }}"
      password: "{{ env_var('password') }}"
      port: "{{ env_var('port') }}"
      database: TEST_STAGE
      schema: {public} # default, macro will manage this
      threads: 16
    prod:
      type: {adapter_type}
      host: "{{ env_var('host') }}"
      user: "{{ env_var('user') }}"
      password: "{{ env_var('password') }}"
      port: "{{ env_var('port') }}"
      database: PROD_STAGE
      schema: {public} # default, macro will manage this
      threads: 16
```

tab: Snowflake

```yaml
{project_name}:
  target: dev
  outputs:
    dev:
      type: {adapter_type}
      account: "{{ env_var('account') }}"
      authenticator: {auth_type}
      user: "{{ env_var('user') }}"
      private_key: "{{ env_var('private_key') }}" # use a key-pair auth if possible
      role: "{{ env_var('role') }}"
      database: DEV_STAGE
      schema: {public} # default, macro will manage this
      warehouse: {warehouse}
      threads: 16
    test:
      type: {adapter_type}
      account: "{{ env_var('account') }}"
      authenticator: {auth_type}
      user: "{{ env_var('user') }}"
      private_key: "{{ env_var('private_key') }}" # use a key-pair auth if possible
      role: "{{ env_var('role') }}"
      database: TEST_STAGE
      schema: {public} # default, macro will manage this
      warehouse: CICD_WH
      threads: 16
    prod:
      type: {adapter_type}
      account: "{{ env_var('account') }}"
      authenticator: {auth_type}
      user: "{{ env_var('user') }}"
      private_key: "{{ env_var('private_key') }}" # use a key-pair auth if possible
      role: "{{ env_var('role') }}"
      database: PROD_STAGE
      schema: {public} # default, macro will manage this
      warehouse: {warehouse}
      threads: 16
```

~~~~


### generate_schema_name

The outputs above differ in `database` and nothing else. That is deliberate: the
**environment is the database, the schema is the layer**, so a schema name is
identical in every environment and nothing downstream carries the environment as
a string. Every source, every `ref`, and every hand-written query against the
warehouse stays byte-identical between targets, and switching environment is a
change of connection only.

The macro therefore has nothing to add to the name — but it still has to exist,
because dbt's default prefixes the custom schema with the profile's `schema:`
and would build `public_staging`:

```sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is not none -%}
        {{ custom_schema_name | trim }}
    {%- elif node is not none and node.resource_type == 'model' -%}
        {{ exceptions.raise_compiler_error(
            "No +schema configured for model '" ~ node.name ~ "'"
        ) }}
    {%- else -%}
        {{ target.schema | trim }}
    {%- endif -%}
{%- endmacro %}
```

Two details in that body:

- Raise **only** for models. dbt resolves a schema for every node it parses, and
  tests carry no `+schema:` of their own, so raising unconditionally breaks
  `dbt test`. The `else` branch is what tests land on.
- Raising at all is worth it: a model whose directory has no matching `models:`
  block in `dbt_project.yml` otherwise builds silently into the profile's
  schema, which is the kind of thing you find weeks later.

The alternative — one database, schemas prefixed `dev_` / `prod_` — reads worse
(`dev_stage.dev_staging`) and puts the environment into every source definition.
The only thing it buys is cross-environment queries in one connection, which on
Postgres is impossible anyway.

## Environment Variables

- shell environment overrides all
- every credential in `profiles.yml` is read through `env_var()`, never hardcoded

> [!warning] Fusion only, revisit later
> A `.env` file gets auto detected by dbt Fusion. Core does not read one, so export the variables in the shell (or wrap the command in something like `dotenv`) before running dbt. Revisit if Fusion ever becomes the main engine — see the Fusion note in [Setup](001-setup.md).

> [!warning] Quote the values
> If a Makefile or script sources the `.env` (`set -a; . ./.env; set +a`), the
> shell interprets the values. A password containing `&`, `^`, or `$` breaks the
> run with a misleading `password authentication failed`, or a
> `command not found` for a fragment of the password. Single-quote every value.

## Seeds

Avoid seeds like if it were the plague. The only time I'd ever use a seed is for patch work. When some mapping table is so small that setting up a source to ingest later (writing code to pipeline the map table) is the better choice in that moment. 

Even if you do use seeds, always make sure to make a source for the table and build or update a pipeline for it.

The reason I don't like seeds is because it's easy to get stale. Also, it can be the cause of errors when building in different environments.

***

[Last modified: 2026-09-02]{.note-modified}
