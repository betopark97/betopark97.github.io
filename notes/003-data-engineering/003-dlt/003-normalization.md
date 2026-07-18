---
title: Normalization
---
dlt by default normalizes api responses.

rule: lists -> child tables, objects -> flattened columns
this means that: 
[
	foo: "bar",
]
becomes table__foo

***

[Last modified: 2026-07-14]{.note-modified}
