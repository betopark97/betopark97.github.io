---
title: Tests
---
The four kinds of data test and where each one is declared are in [Naming](003-naming.md). This page is about what we actually test for.

## Generic Tests

Declared inline in `_{layer}__models.yml`, on the column they apply to. `unique` and `not_null` on every primary key, `relationships` on every foreign key, `accepted_values` on anything enum-like that staging categorized. The yaml formatting for these is in [Styling](004-styling.md).

## Singular Tests

The tests that go under the `dbt_project/tests/` is for conservation tests (at least that's what I do).

- Test Distinct Dimensional Integrity (row counts)
	- test for expected number of rows against actual number of rows
- Test Metric Invariance (aggregate conservation)
	- test for expected agg against actual agg

Both are inter-intra layer checks: the point is that a row or a sum that existed in staging still exists, unchanged, once it reaches a mart. Generic tests cannot express that, which is what makes these singular.

Named `assert_{domain}__{condition}.sql`.

## Where Tests Run

`dbt build` interleaves tests with the models they belong to, so a failed test stops the downstream build instead of letting it run on bad data. See [Workflow](012-workflow.md).

***

[Last modified: 2026-10-18]{.note-modified}
