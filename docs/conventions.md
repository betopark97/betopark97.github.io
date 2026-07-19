# Project Conventions

Structural conventions this repo expects. `scripts/sync_notes.py` relies on them
to order sections, pull metadata, and build the sidebar + gallery — so following
them is what keeps the Notes section "author in Obsidian, everything else
automatic."

Today these conventions cover the **Notes** and **Blog** sections (both
vault-synced, by `scripts/sync_notes.py` and `scripts/sync_blog.py`). Other
sections (`projects/`) are hand-edited; see the bottom of this file.

---

## Notes

The Notes section is generated from the Obsidian vault at `$OBSIDIAN_VAULT_NOTES`
by `scripts/sync_notes.py` (run via `make sync-notes`). **Author in the vault;
never hand-edit `notes/` in the repo** — it's a one-way mirror and gets
overwritten.

All conventions below apply to the **vault** layout.

> **Strict gate.** The sync is not a blind mirror — a node is synced *only if
> it satisfies these conventions*, so a malformed note never reaches Quarto.
> A leaf note that breaks a rule is skipped; a folder that breaks a rule (bad
> name, missing `index.md`, or an `index.md` missing required fields) is
> skipped **whole**, subsections and all. Skips print a one-line reason during
> any sync; `make sync-notes` prints the full PASS/FAIL report. Nothing is
> lost — Obsidian is the source of truth; a skipped note simply won't publish
> until you fix what the report flags.

### 1. Folders: numbered + kebab-case

Every folder — both a top-level **category** and a nested **subsection** — is
named:

```
NNN-slug
```

- **`NNN`** — a **3-digit, zero-padded** number (`001`, `002`, … `010`). It sets
  the order in the sidebar and the gallery. Sorting is lexicographic, so the
  zero-padding matters (`010` must not become `10`).
- **`slug`** — lowercase **kebab-case**: words joined by `-`, no spaces, no
  underscores, no `&` or other punctuation.

| ✅ Good | ❌ Avoid | Why |
|---|---|---|
| `001-terminal` | `terminal` | missing number → unordered |
| `002-snowflake` | `snowflake` | — |
| `001-git-github` | `001-git_github` | underscore, not kebab |
| `003-data-engineering` | `google-cloud-console` | no number prefix |
| `007-spec-kit` | `spec-kit` | no number prefix |

Subfolders nest one level and render as collapsible sub-sections in that
category's sidebar.

### 2. Every folder has an `index.md`

Each folder **must contain an `index.md`** — its landing page and metadata
source. A folder with no `index.md` is skipped whole (the gate can't build a
section without it). Frontmatter:

```yaml
---
title: "Data Engineering"
description: "Data modeling, Snowflake, and dbt."
icon: diagram-3
---

Body text becomes the section's landing-page overview.
```

| Field | Required on | Used for |
|---|---|---|
| `title` | every folder | sidebar label, gallery card title, page `<h1>` |
| `description` | top-level categories | gallery card text + SEO `<meta>` (hidden as on-page subtitle) |
| `icon` | top-level categories; optional on subsections and leaf notes | gallery card icon (category) / sidebar icon (subsection *and* leaf note) |

Notes:

- **No emoji in `title`.** Titles are plain text; the visual icon comes from
  `icon:`. (Emoji in the title would leak into the sidebar and page heading.)
- Subsections need only `title`. An `icon:` on a subsection **is** rendered — as
  that section's icon in the sidebar (same `icon:` rules as below). A
  `description:` on a subsection is unused today.
- **Leaf notes can carry an `icon:` too**, rendered next to their sidebar
  entry — so a single note gets an icon without needing to be promoted to a
  folder + `index.md`. Same `icon:` rules as below (see `009-devtools/`, where
  each tool is a plain file with its own logo). If a note nested inside an
  iconed subsection also sets `icon:`, the note's own icon wins for its row.

#### Picking an `icon:`

Two icon systems are wired in, and the **shape of the value** decides which —
the presence of a colon is the whole distinction:

| Write | Renders via | Example |
|---|---|---|
| a **bare** name (no colon) | **Bootstrap Icons** — native to Quarto | `icon: diagram-3` |
| a **`set:name`** id (has a colon) | **Iconify** — brand logos and any other set | `icon: logos:snowflake-icon` |

**Bootstrap (bare name).** [Bootstrap Icons](https://icons.getbootstrap.com/) is
the icon set Quarto **ships natively** — it bundles the font on every page — so
you write the name with **no prefix at all** (not even `bi:`), just the part
after `bi-` that the site shows:

```yaml
icon: cloud          # ☁  → renders <i class="bi bi-cloud">
icon: diagram-3      # ⛓  pipelines / nodes
icon: hdd-rack       # 🗄  server rack
```

These are free, instant, and offline — nothing is fetched.

**Iconify / shadcn logos (`set:name`).** For anything Bootstrap lacks — brand
logos especially — use a full **Iconify id**, which always has a set name, a
colon, then the icon name. Quarto doesn't know these natively; the repo loads
the [Iconify](https://iconify.design/) web component to render them (fetched
from Iconify at load, then cached). Browse
[icon-sets.iconify.design](https://icon-sets.iconify.design/) or shadcn.io — the
brand-logo set is `logos`:

```yaml
icon: logos:snowflake-icon   # Snowflake brand mark
icon: logos:dbt-icon         # dbt brand mark
icon: logos:fastapi-icon     # FastAPI brand mark
icon: simple-icons:duckdb    # other Iconify sets work too
```

Notes:

- **The colon is the switch:** no colon → Bootstrap (native, bundled); a colon →
  Iconify (fetched). Don't add `bi:` to a Bootstrap name — bare is what routes it
  to the native font.
- shadcn.io shows a logo as `logos-snowflake`; here you write it with a **colon**
  (`logos:snowflake-icon`). The `-icon` square variants read best in the small
  slot.
- Sanity-check any Iconify id by opening
  `https://api.iconify.design/logos/snowflake-icon.svg` — if it shows the logo,
  it'll render.
- A misspelled Bootstrap name or bad Iconify id simply renders nothing — no
  breakage.

### 3. Files: numbered + kebab-case

Leaf note files follow the same rule as folders:

```
NNN-slug.md
```

- 3-digit prefix for order (`001-zshrc.md`, `002-zprofile.md`).
- kebab-case slug, lowercase, no underscores/spaces/`&`.
- The filename (minus `.md`) becomes the page's URL, so keep it clean.
- The sidebar label comes from the file's own `title:` frontmatter, independent
  of the filename — e.g. `001-zshrc.md` can have `title: .zshrc`.

| ✅ Good | ❌ Avoid |
|---|---|
| `001-rbac.md` | `rbac.md` (no number) |
| `003-create-snippets.md` | `create_snippets.md` (no number, underscores) |
| `001-setup.md` | `001-Setup.md` (capitalized) |
| `001-ci-cd.md` | `git_stash_&_wip_commit.md` (underscores, `&`, spaces) |

### 4. The Notes root `index.md`

The vault's top-level `notes/index.md` (not inside any category) is the
**gallery intro**. Its body text is synced into the gallery landing page, above
the category cards. Its frontmatter is not used — the gallery's listing config
lives in the repo (`notes/index.md` there is a hand-authored shell the script
fills in).

### 5. Horizontal-rule dividers need blank lines around them

Markdown's `---` is overloaded. At the **top of a file** it's the YAML
frontmatter fence — expected and fine. But a bare `---` used as a **section
divider** in the body must have a blank line both **before and after** it:

```markdown
some paragraph

---

next section
```

- **No blank line _after_ the `---`** is the dangerous one: Quarto reads the
  `---` plus the following text as a *second* YAML metadata block and the whole
  render dies with `YAMLException: can not read a block mapping entry … (n:1)`.
- **No blank line _before_ the `---`** silently turns the preceding line into a
  setext `<h2>` heading.

When in doubt, use `***` instead — it's a horizontal rule in both Obsidian and
Quarto and is never mistaken for YAML. A file with an unfenced divider is
**skipped by the gate** (and flagged in the `make sync-notes` report), since it
would otherwise crash the render.

### 6. Mermaid diagrams: write ` ```mermaid `, published as `.qmd`

Author diagrams with Obsidian's plain ` ```mermaid ` fence — Obsidian previews
it natively. Quarto, however, only renders the braced form ` ```{mermaid} `,
and only in `.qmd` files (a diagram cell in a `.md` aborts the render with
"You must use the .qmd extension for documents with executable code").

The sync handles the translation: a note (or blog post) containing a mermaid
fence — either spelling — is normalised to ` ```{mermaid} ` and written out as
`.qmd` instead of `.md`. The output URL is unchanged (both render to the same
`.html`). Caveat: this applies to leaf notes and posts only — folder `index.md`
files are copied verbatim, so keep diagrams out of index pages.

---

## Blog

The Blog section is generated from the Obsidian vault at `$OBSIDIAN_VAULT_BLOG`
by `scripts/sync_blog.py` (run via `make sync-blog`). **Author in the vault;
never hand-edit `blog/posts/` in the repo** — it's a one-way mirror and gets
overwritten. Unlike Notes, the blog is a dated *listing* (newest first), not a
topic taxonomy, so the conventions differ.

### 1. Vault layout

```
$OBSIDIAN_VAULT_BLOG/
  index.md          # optional intro prose for the blog landing page
  posts/
    <slug>.md       # one file per post
```

The repo side is generated: `blog/posts/<slug>.md` (mirrored posts) and the
`# >>> auto-blog` sidebar block in `_quarto.yml`. The repo's `blog/index.md` is
a hand-authored shell (the List/Grid listing + tabset); the script only fills
in its intro block.

### 2. Post filenames: kebab-case slug, no number

```
<slug>.md
```

- lowercase **kebab-case**, no spaces/underscores/`&`.
- **No `NNN-` prefix** (unlike Notes) — posts order by **date**, not filename.
- The filename (minus `.md`) becomes the post's URL, so keep it clean and
  descriptive: `choosing-the-right-stack.md` → `…/blog/posts/choosing-the-right-stack.html`.

### 3. Post frontmatter

Author **Quarto-native field names** in Obsidian. The sync translates only what
Obsidian models differently and normalises blanks:

```yaml
---
title: Personal Knowledge Management   # required
date: 2026-06-27                        # required — listing sorts + displays this
description: One-line hook for the listing.   # optional
image: cover.png                        # optional — grid-view thumbnail
tags:                                   # optional — Obsidian Tags property
  - PKM
  - Obsidian
draft: false                            # optional — true hides the post
---
```

| Field | Required? | Notes |
|---|---|---|
| `title` | **yes** | post title; keep it plain ASCII (no emoji) |
| `date` | **yes** | listing **displays and sorts** by this. `date-modified` alone sorts but *won't display* — use `date` |
| `description` | no | listing subtitle; dropped if blank |
| `image` | no | grid-view thumbnail; dropped if blank |
| `tags` | no | Obsidian Tags property → synced to Quarto `categories` (each tag a value) |
| `draft` | no | `true` excludes the post from the listing (Obsidian Checkbox property) |

**Enforcement (the sync is the gate, so the render never fails):**

- A post **missing a required field is skipped** — it never reaches Quarto, so a
  half-finished post can't break `make render` / the deploy.
- **Blank optional fields are dropped** (a null `description:`/`image:` would
  otherwise fail Quarto's schema).
- `make sync-blog` prints a dbt-style **PASS/FAIL report** naming exactly which
  required fields a skipped post is missing — fix them in Obsidian and re-run.

### 4. The Blog root `index.md` (optional intro)

The vault's `blog/index.md` is optional. Its **body** (frontmatter is ignored)
is synced into the intro block of the repo's blog landing page, above the
List/Grid tabs — the same mechanism as the Notes gallery intro. Leave it empty
and the landing page is just the title + listing; add a sentence or two and it
shows as a blurb. No metadata is required there.

### 5. Horizontal-rule dividers need blank lines around them

Same rule as Notes (§5 above): a body `---` divider must have a blank line both
before and after it, or use `***`. `make sync-blog` flags violations in the
report.

---

## Other sections (hand-edited, not vault-synced)

| Section | Convention |
|---|---|
| `projects/<slug>/index.md` | Hand-edit in the repo. Add a sidebar entry under `sidebar.id: projects` in `_quarto.yml`. |
