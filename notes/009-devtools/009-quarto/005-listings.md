---
title: Listings
---
A listing collects documents and renders them as a table, grid, or custom markup. It is declared in the frontmatter of the page that displays it.

In the page's frontmatter, between its `---` fences:

```yaml
title: "Blog"
listing:
  id: posts
  contents: posts
  sort: "date desc"
  fields: [title, date, reading-time, description, categories]
  categories: false
  sort-ui: false
  filter-ui: false
```

Then in the body, an empty div carrying the same id:

```markdown
::: {#posts}
:::
```

The `id` and the empty div with a matching `#id` are what place the output; without the div, Quarto appends the listing at the end of the page.

| Key | Effect |
| --- | --- |
| `contents` | directory, glob, or explicit list of files/metadata to collect |
| `type` | `default`, `table`, `grid`, or omitted when `template` is set |
| `sort` | field plus `asc`/`desc`; multiple criteria allowed |
| `fields` | which item fields are available and displayed |
| `categories` | render a category index (`true`, `numbered`, `cloud`, `unnumbered`) |
| `sort-ui` / `filter-ui` | show Quarto's own sort and filter controls |
| `max-items` | cap the number rendered |
| `feed` | generate an RSS feed |

## Item fields

Each collected document contributes its frontmatter as fields. `title`, `date`, `description`, `author`, `image`, and `categories` (from the document's `categories` key) are standard. Quarto also computes `reading-time` for listing items — it is a listing-level field, not something available inside the document itself.

A post is excluded by setting `draft: true` in its frontmatter.

## Custom templates

`template` points at an [EJS](https://ejs.co/) file that receives the collected items and emits markup:

```yaml
listing:
  template: assets/ejs/card.ejs
```

The template gets an `items` array; each element exposes the fields named in `fields`, plus `path` for the item's URL. A field whose name contains a hyphen must be read with bracket syntax:

```
<% for (const item of items) { %>
  <a href="<%= item.path %>">
    <span><%= item.title %></span>
    <% if (item['reading-time']) { %><span><%= item['reading-time'] %></span><% } %>
  </a>
<% } %>
```

Wrapping the template body in a ```` ```{=html} ```` block passes it through as raw HTML rather than letting Pandoc reparse it.

Setting `template` replaces the built-in rendering, which means Quarto's `sort-ui`, `filter-ui`, and category index no longer apply to the output. Any interaction — filter buttons, for example — has to be supplied alongside the template.

***

[Last modified: 2026-08-30]{.note-modified}
