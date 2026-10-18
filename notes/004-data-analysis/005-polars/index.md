---
title: Polars
description: "Columnar DataFrames with a lazy API, the default over pandas."
icon: simple-icons:polars
---
Polars is a columnar DataFrame library with a lazy expression API. It is the
default choice over pandas for anything that has to fit in a container: strings
stay in Arrow rather than becoming Python objects, so real-world frames land
roughly 4× smaller, and `pl.from_arrow` on a Snowflake `fetch_arrow_all()` skips
a materialisation entirely.

These pages cover porting existing pandas code without silently changing the
numbers it produces.

## Reading Path

| Page | What it answers |
| --- | --- |
| [Porting from pandas](001-porting-from-pandas.md) | the semantic differences that change results rather than raising |
