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

`.github/workflows/publish.yml` runs on three triggers, and behaves slightly differently per trigger:

| Trigger | Behavior |
|---|---|
| `push` to `main` | Fetch about-me (strict) → setup Quarto → render → publish to `gh-pages` → Discord notify |
| `workflow_dispatch` (Actions → Run workflow) | Same as push |
| `schedule` (00:00 UTC / 09:00 KST daily) | Curl previously-deployed `_aboutme.md` from live site → fetch fresh README → diff. **If unchanged → skip everything after**, finish in ~10s with a green check, no `gh-pages` commit. **If changed → render + publish + notify**, same as push. |

The cron exists to refresh the about-me block (pulled from the GitHub profile README) without you having to push or click anything. Most scheduled runs are no-ops; only real README edits produce a deploy.

Typical wall time from `git push` to live site: 1–2 minutes. Scheduled no-op runs finish in ~10 seconds.

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

#### Empty placeholder section

If you want the section header to appear in the sidebar *before* you've written any pages for it, you can't use `auto:` — it errors on empty folders. Use a bare `section:` block with an empty `contents:` list instead:

```yaml
- section: "Time Series"
  contents: []
```

When you write the first `.qmd` in that folder, **replace the whole `section:` block with `- auto: "notes/time-series"`** — don't keep the wrapper around the `auto:`, or you'll get a double-nested "Time Series > Time Series" in the sidebar (because `auto:` already derives its own header from the folder name).

### Other sections

| Where | What |
|---|---|
| `projects/<slug>/index.qmd` | New project. Add an entry under `sidebar.id: projects`. |
| `blog/<post-name>.qmd` | New blog post. **No `_quarto.yml` edit needed** — the blog sidebar uses `contents: blog/` and auto-includes every `.qmd`. |

### File-naming conventions

- **Order**: numeric prefix (`00-`, `01-`, ...). Alphabetic sort = intended order.
- **Label**: each file's frontmatter `title:` — independent of filename.
- **URL slug**: the filename (minus extension), so use kebab-case, no `&`, no spaces.

## Dynamic about-me block

The Home page (`index.qmd`) hero is pulled from the GitHub profile README at `betopark97/betopark97`. Flow:

1. `scripts/fetch-aboutme.sh` curls `raw.githubusercontent.com/.../README.md` into `assets/_aboutme.md`. The file is gitignored — it's regenerated on every build.
2. `_quarto.yml` declares `assets/_aboutme.md` as a resource, so Quarto copies it verbatim to `_site/assets/_aboutme.md` during render.
3. `index.qmd` splices it into the page via `{{< include assets/_aboutme.md >}}`.
4. After publish, the live site serves the raw markdown at `https://betopark97.github.io/assets/_aboutme.md` — which is what the next cron tick diffs against.

**To edit the content**: push to `betopark97/betopark97/README.md`. Live site updates within 24h via the cron, or instantly if you trigger `workflow_dispatch`.

**Script behavior**: `STRICT=1` makes the script exit non-zero on fetch failure (used in CI to prevent shipping a placeholder). Without `STRICT`, it soft-fails — reuses any existing `_aboutme.md`, or writes a placeholder. Local `make render` uses the soft-fail path so offline dev still builds.

## Discord notifications

The publish workflow pings a Discord webhook on:

- **Deploy success** — only when something actually shipped (skip on no-change cron ticks).
- **Workflow failure** — any step failure, on any trigger.

**Setup** (one-time):

1. In Discord: channel ⚙️ → Integrations → Webhooks → New Webhook → Copy URL.
2. In repo: Settings → Secrets and variables → Actions → New repository secret. Name: `DISCORD_WEBHOOK_URL`. Value: the URL.

If the secret isn't set the notify steps log "No DISCORD_WEBHOOK_URL set; skipping" and exit clean — deploys still work, you just get no pings.

## Styling

Theme is split across two SCSS files in `_quarto.yml` → `format.html.theme`:

- **`assets/scss/catppuccin-mocha.scss`** — palette ($ctp-* variables), Bootstrap variable overrides, and color/typography skin for framework-provided elements (navbar, sidebar, code, tables, headings).
- **`assets/scss/styles.scss`** — structural rules (borders, padding, layout) and custom components (e.g. `.resume-entry`).

Quarto merges `scss:defaults` across both files, so `styles.scss` can reference `$ctp-*` palette variables without re-declaring them.

When adding styles: reach for plain markdown first (italic, bold, lists, blockquote). Only introduce SCSS classes when markdown can't express what you need. New custom-component rules go in `styles.scss`, not the theme file.

## Common tweaks

- **Navbar items / order**: `website.navbar.right`.
- **Footer**: `website.page-footer`.
- **Analytics / meta tags**: `assets/html/custom_header.html`.

## Troubleshooting

- **CI fails on render**: open the Actions tab on GitHub and read the log. Usually broken `.qmd` syntax, a missing image path, or a typo in `_quarto.yml`.
- **Pages serves wrong content**: re-check Settings → Pages still points to `gh-pages` / `/(root)`.
- **Local render works, CI fails**: typically a case-sensitivity issue. macOS is case-insensitive; the Linux runner isn't. Check the exact casing of every filename referenced in `href:` paths.
- **Stale browser**: hard-refresh (Cmd+Shift+R) — GitHub Pages aggressively caches.
