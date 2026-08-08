# Data Modeling

we will follow Kimball’s three layered data warehouse

staging, intermediate, marts\
bronze, silver, gold

staging is for renames, data types, and variant normalization only and a data contract will be applied to these

the intermediate is for all transformations

the gold stage is for dim and fact tables\
bi and semantics as views\
a data contract is also applied to the gold stage

------------------------------------------------------------------------

Last modified: 2026-08-04

Back to top
