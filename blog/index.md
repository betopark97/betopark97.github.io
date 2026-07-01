---
title: "Blog"
listing:
  - id: blog-list
    type: default
    contents: posts
    sort: "date desc"
    fields: [title, date, reading-time, description, categories]
    date-format: "iso"
    categories: true
    sort-ui: false
    filter-ui: false
  - id: blog-grid
    type: grid
    contents: posts
    sort: "date desc"
    fields: [title, date, reading-time, description, categories]
    date-format: "iso"
    sort-ui: false
    filter-ui: false
---

<!-- >>> blog-intro (synced from the Obsidian Blog index.md by scripts/sync_blog.py) -->
> "Writing is thinking. To write well is to think clearly. That's why it's so hard." — David McCullough

Half-formed ideas, worked out in public — notes that grew up enough to share.
<!-- <<< blog-intro -->

::: {.panel-tabset}

## List

::: {#blog-list}
:::

## Grid

::: {#blog-grid}
:::

:::
