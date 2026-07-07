---
title: Conventions
---
add foldabble examples
add full project tree example

> [!NOTE]- Example
> asdf

## Project Level Meta Files

`dbt_project.yml`

`packages.yml`

`profiles.yml`

## Directory Names

`models/{domain}/{layer}`

## Meta Names

`_{layer}__{sources|models}.yaml`

The main characteristic of meta yaml files is that the naming starts with an underscore/underbar.

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

[Last modified: 2026-06-30]{.note-modified}
