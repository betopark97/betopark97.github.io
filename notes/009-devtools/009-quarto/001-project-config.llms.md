# Project Config

`_quarto.yml` at the project root defines the project. Its presence is what makes a directory a Quarto project rather than a set of standalone documents.

## Project block

``` numberSource
project:
  type: website
  output-dir: _site
```

`type` selects the project kind — `default`, `website`, `book`, or `manuscript`. It determines which extra config blocks are recognised: a `website` project reads a `website:` block, a book reads `book:`.

`output-dir` is where the rendered site is written. It is cleaned and rewritten on render, so nothing hand-authored should live there.

## Choosing inputs

By default a project renders every `.qmd`, `.md`, `.ipynb`, `.rmd` it finds, skipping directories that begin with `.` or `_`. An explicit `render` list overrides that:

``` numberSource
project:
  render:
    - "*.qmd"
    - "*.md"
    - "!README.md"
    - "!docs/"
```

Entries are globs evaluated in order. A leading `!` negates, removing previously matched files. Because the defaults already skip dot- and underscore-prefixed directories, files under `.github/` or `_extensions/` never need excluding.

A markdown file that is not meant to be a page — a README, contributor docs — will otherwise be rendered and published, since `*.md` matches it.

## Resources

Quarto copies an asset to the output directory when it can see a reference to it: an image in markdown, a stylesheet in `theme`. Files referenced only from raw HTML or from JavaScript are invisible to that scan and must be declared:

``` numberSource
project:
  resources:
    - assets/data.json
    - assets/js/late-loaded.js
```

Each entry is a path or glob relative to the project root, copied verbatim into `output-dir`.

## Execution and freeze

For projects with executable code, `execute:` controls evaluation, and `freeze` caches results so documents are not re-executed on every render:

``` numberSource
execute:
  freeze: auto
```

`auto` re-executes only when the source changes; `true` never re-executes; `false` always does. Frozen results are stored in `_freeze/` and are meant to be committed, so a CI render does not need the computational environment.

## Config precedence

Settings resolve from narrowest to widest: keys in a document’s own frontmatter beat a `_metadata.yml` in its directory, which beats `_quarto.yml`. See [Directory Metadata](../../../notes/009-devtools/009-quarto/008-directory-metadata.llms.md).

------------------------------------------------------------------------

Last modified: 2026-08-30

Back to top
