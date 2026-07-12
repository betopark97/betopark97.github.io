---
title: Conventions
---
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
│       │   ├── _stg__sources.yaml     # Source db/schema + origin docs
│       │   ├── _stg__models.yaml      # Models, columns, tests, descriptions
│       │   └── stg_{domain}__{entity}.sql
│       ├── intermediate/
│       │   ├── _int__models.yaml
│       │   └── int_{domain}__{entity}.sql
│       └── mart/
│           ├── _mart__models.yaml
│           └── mart_{domain}__{entity}.sql
├── seeds/                             # Static CSV reference data
├── snapshots/                         # SCD type-2 snapshots
├── target/                            # Compiled SQL & artifacts (git-ignored)
├── tests/                             # Singular (complex) data tests
│   └── assert_{domain}__{condition}.sql
├── .env                               # Env vars (dbt fusion auto-detect, git-ignored)
├── .gitignore
├── dbt_project.yml                    # Project config
└── packages.yml                       # Package dependencies
```

Below we'll discuss what each component is and how to fill them in.

## Project Level Meta Files

> [!example]- `dbt_project.yml`
> asdf

> [!example]- `packages.yml`

> [!example]- `profiles.yml`

## Directory Names

`models/{domain}/{layer}`

## Meta Names

`_{layer}__{sources|models}.yaml`

The main characteristic of meta yaml files is that the naming starts with an underscore.

The sources yaml file is needed only in the staging layer. It contains the source database and schema. Also  a brief documentation of the origin of the data.

The models yaml file is needed in every layer. It contains models, columns, data tests along with descriptions where needed.

The data tests are generic (singular) tests and custom tests, package tests.
- singular tests include: `unique`, `not null`, `accepted_values`, `relationships`
- custom tests consist of macros
- package tests consist of `dbt_utils` and other community packages

## Model Names

`{layer}_{domain}__{entity}_{temp}.sql`

## Tests Names

The test sql files are for complex data quality tests that cannot be covered with generic (built-in) tests also called singular tests. This includes tests like data conservation inter-intra layers.

## Incremental Models

only use merge, it's the only idempotent closes to "set-it-and-forget-it".
remember to add the logic to erase orphaned data.

if the data is too big for merge, then use delete+insert or insert_overwrite
delete+insert checks for a set of keys that you define

## Environment Variables

- shell environment overrides all
- `.env` file is auto detected with the new dbt fusion

## Models

- all lower case
- no select stars

***

[Last modified: 2026-07-12]{.note-modified}
