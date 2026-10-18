# dbt

Transforming warehouse data in SQL with dbt Core: project layout, layers, tests and runs.

This dbt guide / note will be updated to follow the most stable version of the dbt-core package.\
This means that this section does not cover paid services like dbt Cloud or paid features (or freemium) like dbt State.

Current version: dbt Core v1.11

These pages cover the conventions and best practices I’ve set up when working with dbt, including the best practices from the official documentation, and they double as a boilerplate for getting a new project started.

## Reading Path

| Page | What it answers |
|----|----|
| [Setup](../../../notes/003-data-engineering/005-dbt/001-setup.llms.md) | how do I install dbt and which packages do I add |
| [Project Structure](../../../notes/003-data-engineering/005-dbt/002-project-structure.llms.md) | what goes where on disk, and what fills `dbt_project.yml`, `packages.yml`, `profiles.yml` |
| [Naming](../../../notes/003-data-engineering/005-dbt/003-naming.llms.md) | what do I call this file, schema, yaml, or test |
| [Styling](../../../notes/003-data-engineering/005-dbt/004-styling.llms.md) | how do I write the SQL, jinja, and yaml inside it |
| [Layers](../../../notes/003-data-engineering/005-dbt/005-layers.llms.md) | which layer does this transformation belong to |
| [Staging](../../../notes/003-data-engineering/005-dbt/006-staging.llms.md) | bronze |
| [Intermediate](../../../notes/003-data-engineering/005-dbt/007-intermediate.llms.md) | silver |
| [Marts](../../../notes/003-data-engineering/005-dbt/008-marts.llms.md) | gold |
| [Materializations & Build Time](../../../notes/003-data-engineering/005-dbt/009-materializations.llms.md) | view, table, or incremental, and how to keep builds fast |
| [Tests](../../../notes/003-data-engineering/005-dbt/010-tests.llms.md) | what do I test for |
| [Documentation](../../../notes/003-data-engineering/005-dbt/011-documentation.llms.md) | catalog, contracts, lineage, access control |
| [Workflow](../../../notes/003-data-engineering/005-dbt/012-workflow.llms.md) | which command do I run, and where does a flag go |
| [Node Selection](../../../notes/003-data-engineering/005-dbt/013-node-selection.llms.md) | which nodes does that command touch |
| [CI/CD](../../../notes/003-data-engineering/005-dbt/014-ci-cd.llms.md) | what runs on a pull request |
| [Orchestration](../../../notes/003-data-engineering/005-dbt/015-orchestration.llms.md) | what runs on a schedule |

If you are writing a model right now, the short path is [Layers](../../../notes/003-data-engineering/005-dbt/005-layers.llms.md) to pick the layer, then that layer’s page, with [Naming](../../../notes/003-data-engineering/005-dbt/003-naming.llms.md) and [Styling](../../../notes/003-data-engineering/005-dbt/004-styling.llms.md) open alongside.

Back to top
