# Development Workflow

## Local editing: `preview` vs `render`

| Command | What it does |
|---|---|
| `quarto preview` | Build **and serve** on `http://localhost:<port>` with hot reload. Use while editing. |
| `quarto render`  | Build once to `_site/` and exit. Use for one-shot inspection or scripts. |

Both produce identical output. `preview` is just `render` + dev server + file watcher wrapped together. CI uses `render`.

## Branching model

- **`dev`** — working branch. All edits start here.
- **`main`** — production. CI publishes only from `main`.
- **`gh-pages`** — built site. **Never edit manually**; CI overwrites it on every deploy.

## Day-to-day flow

```bash
# 1. work on dev
git switch dev
# ...edit .qmd files...
quarto preview                # iterate live
git add <files>
git commit -m "..."

# 2. integrate to main
git switch main
git pull                      # in case anything landed remotely
git rebase dev                # or: git merge --ff-only dev

# 3. push
git push origin main
```

The push to `main` triggers `.github/workflows/publish.yml`:

1. Checks out the repo
2. Installs Quarto
3. Runs `quarto render` → `_site/`
4. Pushes contents to the `gh-pages` branch
5. GitHub Pages serves the new content

Typical wall time from `git push` to live site: 1–2 minutes.

## Verifying a deploy

```bash
gh run list --limit 3                                      # CI run status
gh api repos/betopark97/betopark97.github.io/pages         # Pages config
```

Or just visit https://betopark97.github.io/ and hard-refresh.

## Adding content

`_quarto.yml` only defines the **hierarchy** (which sections exist and in what order). Files and labels inside each section come from the folder.

### Add a new page to an existing section under Notes

Drop a file into the section's folder. The numeric prefix controls order; the frontmatter `title:` controls the sidebar label.

```
notes/data-analysis/03-modeling.qmd
---
title: "Modeling"
---
```

No `_quarto.yml` edit needed.

### Add a new section under Notes

1. Create a folder under `notes/` with a kebab-case name (e.g. `notes/time-series/`).
2. Drop files in with numeric prefixes (`00-intro.qmd`, `01-...`).
3. In `_quarto.yml`, add one line under `sidebar.id: notes` → `contents:`:

   ```yaml
   - auto: "notes/time-series"
   ```

The section title is auto-derived from the folder name (`time-series` → "Time Series"). To override (e.g. "Time Series Analysis"), add `_metadata.yml` inside the folder:

```yaml
title: "Time Series Analysis"
```

### Other sections

| Where | What |
|---|---|
| `projects/<slug>/index.qmd` | New project. Add an entry under `sidebar.id: projects`. |
| `blog/<post-name>.qmd` | New blog post. **No `_quarto.yml` edit needed** — the blog sidebar uses `contents: blog/` and auto-includes every `.qmd`. |

### File-naming conventions

- **Order**: numeric prefix (`00-`, `01-`, ...). Alphabetic sort = intended order.
- **Label**: each file's frontmatter `title:` — independent of filename.
- **URL slug**: the filename (minus extension), so use kebab-case, no `&`, no spaces.

## Styling

Theme is split across two SCSS files in `_quarto.yml` → `format.html.theme`:

- **`theme/catppuccin-mocha.scss`** — palette ($ctp-* variables), Bootstrap variable overrides, and color/typography skin for framework-provided elements (navbar, sidebar, code, tables, headings).
- **`theme/styles.scss`** — structural rules (borders, padding, layout) and custom components (e.g. `.resume-entry`).

Quarto merges `scss:defaults` across both files, so `styles.scss` can reference `$ctp-*` palette variables without re-declaring them.

When adding styles: reach for plain markdown first (italic, bold, lists, blockquote). Only introduce SCSS classes when markdown can't express what you need. New custom-component rules go in `styles.scss`, not the theme file.

## Common tweaks

- **Navbar items / order**: `website.navbar.right`.
- **Footer**: `website.page-footer`.
- **Analytics / meta tags**: `custom_header.html`.

## Troubleshooting

- **CI fails on render**: open the Actions tab on GitHub and read the log. Usually broken `.qmd` syntax, a missing image path, or a typo in `_quarto.yml`.
- **Pages serves wrong content**: re-check Settings → Pages still points to `gh-pages` / `/(root)`.
- **Local render works, CI fails**: typically a case-sensitivity issue. macOS is case-insensitive; the Linux runner isn't. Check the exact casing of every filename referenced in `href:` paths.
- **Stale browser**: hard-refresh (Cmd+Shift+R) — GitHub Pages aggressively caches.
