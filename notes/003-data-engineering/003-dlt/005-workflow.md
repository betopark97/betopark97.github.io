---
title: Workflow
---
## Command Line Interface

`dlt pipeline`

when dev testing and you want to only drop a pipeline

`dlt pipeline {source} drop {table}`

when performing a refresh to changes:

`drop_sources`: Drops all tables in the source + source/resource state. Do it when fixes changed the DDL.

`drop_resources`: Drops tables for only the resources in that run. Also, do it when fixes changed the DDL.

`drop_data`: Truncates rows only (doesn't delete and recreate the table), and schema stays untouched. Honestly, don't think it will be used as the default is it delete + insert and merge strategies already deal with this.

***

[Last modified: 2026-08-09]{.note-modified}
