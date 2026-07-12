---
title: Workflow
---
dbt commands
- dbt debug
- dbt clean
- dbt deps
- dbt run
- dbt test
- dbt build
- dbt seed
- dbt lint (requires .sqlfluff)
- dbt fmt (Coming soon...)


Let's use dbt fusion locally for faster build, run, compilation whatever times.

```
-t | --target
-s | --select
-x | --fail-fast

+model = upstream
model+ = downstream
```

***

[Last modified: 2026-06-26]{.note-modified}
