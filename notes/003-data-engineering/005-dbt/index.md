---
title: dbt
description: "Transforming warehouse data in SQL with dbt Core: project layout, layers, tests and runs."
icon: logos:dbt-icon
---
This dbt guide / note will be updated to follow the most stable version of the dbt-core package.
This means that this section does not cover paid services like dbt Cloud or paid features (or freemium) like dbt State.

Current version: dbt Core v1.11

These pages cover the conventions and best practices I've set up when working with dbt, including the best practices from the official documentation, and they double as a boilerplate for getting a new project started.

## Reading Path

| Page | What it answers |
| --- | --- |
| [Setup](001-setup.md) | how do I install dbt and which packages do I add |
| [Project Structure](002-project-structure.md) | what goes where on disk, and what fills `dbt_project.yml`, `packages.yml`, `profiles.yml` |
| [Naming](003-naming.md) | what do I call this file, schema, yaml, or test |
| [Styling](004-styling.md) | how do I write the SQL, jinja, and yaml inside it |
| [Layers](005-layers.md) | which layer does this transformation belong to |
| [Staging](006-staging.md) | bronze |
| [Intermediate](007-intermediate.md) | silver |
| [Marts](008-marts.md) | gold |
| [Materializations & Build Time](009-materializations.md) | view, table, or incremental, and how to keep builds fast |
| [Tests](010-tests.md) | what do I test for |
| [Documentation](011-documentation.md) | catalog, contracts, lineage, access control |
| [Workflow](012-workflow.md) | which command do I run, and where does a flag go |
| [Node Selection](013-node-selection.md) | which nodes does that command touch |
| [CI/CD](014-ci-cd.md) | what runs on a pull request |
| [Orchestration](015-orchestration.md) | what runs on a schedule |

If you are writing a model right now, the short path is [Layers](005-layers.md) to pick the layer, then that layer's page, with [Naming](003-naming.md) and [Styling](004-styling.md) open alongside.
