# Directory Metadata

A `_metadata.yml` in any directory supplies frontmatter to every document in that directory and below. It is merged into each document’s own frontmatter at render time.

``` numberSource
# posts/_metadata.yml
title-block-banner: true
body-classes: blog-post
toc: false
```

The file uses the same keys a document’s frontmatter would, without the `---` fences.

## Precedence

Narrowest wins. For any single key:

``` numberSource
document frontmatter  >  nearest _metadata.yml  >  parent _metadata.yml  >  _quarto.yml
```

Scalars are replaced. Maps are merged key by key, so a document can override one nested option without restating the rest.

The leading underscore means the file is never treated as an input to render.

## What it is for

Anything that applies to a whole directory but does not belong in the individual files — a shared layout option, a class used to scope styles, a default `format` tweak for one section. It is also the place for options when the documents themselves are generated or mirrored from elsewhere, since edits to those files would not survive regeneration.

------------------------------------------------------------------------

Last modified: 2026-08-30

Back to top
