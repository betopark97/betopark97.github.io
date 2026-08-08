# Data Architecture

Before starting with any project it’s good to have a rough idea on how the architecture will look like for your data platform. However, it takes a lot of time to build up a stable data platform, hence the “rough idea,” and so you should iterate by building something, then testing, deploying to production, and finally optimize (mix up the order a bit if needed like optimizing before deploying, etc.).

Some of the important building blocks to making a stable data platform is the good orchestration of the following:

- DAG design
- dependency management
- SLAs
- task isolation
- transformations
- testing
- lineage
- deployment
- idempotency
- retries
- environment promotion
- recovery / health check (fail safely and recover cleanly)
- backfills
- alerting
- late arriving data
- state management

Back to top
