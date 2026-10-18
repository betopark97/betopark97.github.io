---
title: Naming
---
Every naming rule in the project lives on this page. Field and column naming is a styling concern and lives in [Styling](004-styling.md) instead.

## Directory / Database Names

If it is a multi-domain project: `models/{domain}/{layer}`
If it is a single-domain project: `models/{layer}`

Schema names are singular, model names are plural. The one exception is the gold layer, which is `marts`, not `mart` — dbt's own best-practice guides name it that way and every dbt project reads it that way, so the convention wins over the singular rule. The directory, the schema, and the meta file all say `marts`.

Meta files use the `.yml` extension, not `.yaml`. dbt's own docs and starter project use `.yml`.

## Meta Names

`_{layer}__{sources|models}.yml`

The main characteristic of meta yaml files is that the naming starts with an underscore.

The sources yaml file is needed only in the staging layer. It contains the source database and schema. Also  a brief documentation of the origin of the data.

The models yaml file is needed in every layer. It contains models, columns, data tests along with descriptions where needed.

## Model Names

```text
{layer}_{domain}__{entity}_{temp}_{version}.sql
```

| Slot | Required | Rule |
| --- | --- | --- |
| `{layer}` | yes | `stg`, `int`, `dim`, `fct`, `bridge` |
| `{domain}` | yes | the business domain. **staging is the exception** — it takes the source instead |
| `{entity}` | yes | plural, business terminology, not source terminology |
| `{temp}` | no | temporal grain: `daily`, `monthly`, `weekly` |
| `{version}` | no | `v1`, `v2` |

Note there is no `marts_` prefix. The marts layer is expressed by which of `dim`, `fct`, or `bridge` the model is, so the layer slot already carries it.

```text
stg_api__youtube_views.sql            # source = api, not domain
int_youtube__views.sql                # no grain, no version
int_youtube__views_daily_v1.sql       # all five slots
fct_youtube__views_daily.sql
dim_youtube__channels.sql
bridge_youtube__videos_playlists.sql  # resolves a many-to-many
```

The double underscore separates the domain (or source) from the entity. Single underscores separate everything else, which is what keeps the two halves readable.

## Test Names

Data tests come in four kinds and only one of them is a file you name:

| Kind | Where it lives | Examples |
| --- | --- | --- |
| generic | `_{layer}__models.yml` | `unique`, `not_null`, `accepted_values`, `relationships` |
| custom generic | `macros/` | your own reusable test macros |
| package | `_{layer}__models.yml` | `dbt_utils` and other community tests |
| singular | `tests/` | `assert_{domain}__{condition}.sql` |

Singular tests are bespoke SQL for data quality checks that the generic tests cannot express, like data conservation inter-intra layers. What we use them for is in [Tests](010-tests.md).

***

[Last modified: 2026-10-18]{.note-modified}
