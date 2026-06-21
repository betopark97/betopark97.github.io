# Project Conventions

Structural conventions this repo expects. `scripts/sync_notes.py` relies on them
to order sections, pull metadata, and build the sidebar + gallery — so following
them is what keeps the Notes section "author in Obsidian, everything else
automatic."

Today these conventions cover the **Notes** section (vault-synced). Other
sections (`projects/`, `blog/`) are hand-edited; see the bottom of this file.

---

## Notes

The Notes section is generated from the Obsidian vault at `$OBSIDIAN_VAULT_NOTES`
by `scripts/sync_notes.py` (run via `make sync-notes`). **Author in the vault;
never hand-edit `notes/` in the repo** — it's a one-way mirror and gets
overwritten.

All conventions below apply to the **vault** layout.

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
source. Frontmatter:

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
| `icon` | top-level categories | gallery card icon |

Notes:

- **No emoji in `title`.** Titles are plain text; the visual icon comes from
  `icon:`. (Emoji in the title would leak into the sidebar and page heading.)
- Subsections only need `title`. Adding `description`/`icon` to them is harmless
  and future-proofs (e.g. if sub-galleries are ever added), but they aren't
  rendered today.

#### Picking an `icon:`

`icon:` is a [Bootstrap Icons](https://icons.getbootstrap.com/) name **without
the `bi-` prefix**. On that site, each icon shows as `<i class="bi bi-cloud">`
— copy the part after `bi-`:

```yaml
icon: cloud          # ☁  → renders <i class="bi bi-cloud">
icon: diagram-3      # ⛓  pipelines / nodes
icon: hdd-rack       # 🗄  server rack
```

A misspelled or empty name simply renders no glyph — no breakage.

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

---

## Other sections (hand-edited, not vault-synced)

| Section | Convention |
|---|---|
| `projects/<slug>/index.md` | Hand-edit in the repo. Add a sidebar entry under `sidebar.id: projects` in `_quarto.yml`. |
| `blog/<post>.md` | Hand-edit in the repo. No `_quarto.yml` change needed — the blog sidebar uses `contents: blog/` and auto-includes every `.md`. |
