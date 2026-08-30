# Format and Dialect

`format:` selects the output and its options. A project-level `format` applies to every document; a document can override it in its own frontmatter.

``` numberSource
format:
  html:
    toc: true
    code-line-numbers: true
    html-math-method: katex
```

## Markdown dialect

Quarto reads Pandoc’s markdown, and `from:` selects which extensions are enabled. The value is a Pandoc format spec: a base name followed by `+`/`-` extension toggles.

``` numberSource
format:
  html:
    from: markdown+autolink_bare_uris+hard_line_breaks
```

Two extensions worth knowing because they change how ordinary prose renders:

| Extension | Effect |
|----|----|
| `autolink_bare_uris` | a bare `https://…` becomes a link without `<>` or `[]()` |
| `hard_line_breaks` | a single newline renders as `<br>` instead of being folded into the paragraph |

`hard_line_breaks` matches how Obsidian and most note apps behave. It also means source files must not be soft-wrapped: a paragraph broken across several source lines will render with visible line breaks at each one.

The full extension list is in the [Pandoc manual](https://pandoc.org/MANUAL.html#extensions).

## Common HTML options

| Key | Effect |
|----|----|
| `toc` | render a table of contents; `toc-depth` sets how deep |
| `code-line-numbers` | number lines in highlighted code blocks |
| `code-copy` | copy button on code blocks (`true`, `false`, `hover`) |
| `html-math-method` | math renderer — `katex`, `mathjax`, `webtex` |
| `include-in-header` | file injected into `<head>` on every page |
| `include-before-body` / `include-after-body` | file injected at the start/end of `<body>` |

The `include-*` keys take a path to a file containing raw HTML. `include-after-body` is where a script that needs the DOM present belongs.

## Dates

`date-format` sets how every date is displayed — title blocks, listing items, `date-modified`. It accepts a token string or one of the shorthands `iso`, `short`, `medium`, `long`, `full`.

``` numberSource
date-format: iso
```

Set at project level it applies site-wide, which keeps listing cards and title blocks from disagreeing about format.

------------------------------------------------------------------------

Last modified: 2026-08-30

Back to top
