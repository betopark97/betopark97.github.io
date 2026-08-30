---
title: Lua Filters
---
A Lua filter is a script that rewrites the document's abstract syntax tree between parsing and writing. It is the supported way to add syntax Pandoc does not know, or to transform elements site-wide.

```yaml
filters:
  - assets/filters/first.lua
  - assets/filters/second.lua
```

Listed at project level they run on every document, in list order. A document can add its own with a `filters` key in frontmatter.

## Writing one

Define a function named after an AST element type. It receives the element and returns a replacement, a list of elements, or `nil` to leave it untouched.

```lua
-- Wrap every table so it can scroll on narrow screens.
function Table(tbl)
  return pandoc.Div(
    { tbl },
    pandoc.Attr("", { "table-responsive" })
  )
end
```

Common entry points: `Str`, `Code`, `CodeBlock`, `BlockQuote`, `Table`, `Div`, `Header`, `Link`, `Image`. A `Pandoc(doc)` function receives the whole document and runs last, which is where document-wide work belongs.

`pandoc.Attr(identifier, classes, attributes)` builds the attribute triple every element constructor takes. Constructors mirror the element names: `pandoc.Div`, `pandoc.Para`, `pandoc.Plain`, `pandoc.Str`, `pandoc.RawBlock("html", "…")`.

To reparse a string as markdown rather than emitting it literally:

```lua
local blocks = pandoc.read(text, "markdown").blocks
```

## Ordering

Filters see the AST as the previous filter left it. A filter that creates new elements must run *before* any filter expected to process what it created — a filter that turns a fenced block into nested content has to precede the one that styles code blocks, or the nested code is never visited.

## Quarto specifics

`quarto.doc.input_file` holds the path of the file being rendered, which is the reliable way to scope a filter to a subtree:

```lua
function Pandoc(doc)
  local input = quarto.doc.input_file or ""
  if not input:find("/posts/") then return nil end
  -- …
end
```

Two behaviours that are easy to get wrong:

- **Quarto's own filters run on the initial AST.** Elements a user filter creates afterwards are never seen by them. Emitting a Quarto construct — a callout, a tabset — by producing the div that Quarto's filter *would* have produced does not work; the markup that filter generates has to be emitted directly.
- **Some frontmatter keys never reach `doc.meta`.** Quarto lifts certain keys into template variables before user filters run, so a filter gating on one of them reads an empty value. Gate on the input path instead.

Quarto's Lua API is documented at [quarto.org/docs/extensions/lua-api](https://quarto.org/docs/extensions/lua-api.html); the Pandoc module is documented at [pandoc.org/lua-filters](https://pandoc.org/lua-filters.html).

***

[Last modified: 2026-08-30]{.note-modified}
