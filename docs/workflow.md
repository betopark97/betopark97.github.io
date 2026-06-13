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

Notes live in Obsidian and sync into `notes/`; everything else (`index.md`, `portfolio.md`, `projects/`, `blog/`) is hand-edited in the repo.

### Notes section (Obsidian → repo)

The `notes/` directory is **derived** — `scripts/sync_notes.py` mirrors an Obsidian vault folder into it. Do not hand-edit files under `notes/`; edit in Obsidian and re-sync.

#### One-time setup

Create a `.env` at the project root (gitignored) with the absolute path to the Notes folder inside your vault:

```
OBSIDIAN_VAULT_NOTES=/Users/you/Library/Mobile Documents/iCloud~md~obsidian/Documents/<Vault>/notes
```

No quotes, no backslash escapes — Make's `include` reads the value literally. Spaces are fine, leading `~` is expanded by the script.

#### Vault layout (in Obsidian)

- **Section ordering** — numeric prefix on the folder name: `01-terminal/`, `02-devops/`, …. Without a prefix, sections sort alphabetically after the numbered ones.
- **Nesting** — subfolders inside a section become collapsible sub-sections in the sidebar (e.g. `03-data-engineering/data-modeling/` shows "Data Modeling" nested under "Data Engineering").
- **File ordering within a section** — same numeric-prefix trick on filenames: `00-preface.md`, `01-project-setup.md`, ….
- **Section title** — Quarto title-cases the folder name by default, so `07-ai-engineering/` displays as "07 Ai Engineering". To override (clean prefix + fix acronyms), create an `index.md` in that section's Obsidian folder:
  ```yaml
  ---
  title: "AI Engineering"
  ---

  Section overview goes here.
  ```
  The `index.md` also serves as the section's landing page at `/notes/<slug>/`.
- **File titles** — each note's `title:` frontmatter controls its sidebar label, independent of filename.

#### Sync command

```bash
make sync-notes
```

That single target does the whole pipeline: `make clean` (busts Quarto's incremental cache so sidebar/title changes take effect), then runs the sync script, then `make render`. After it finishes, `_site/` is fresh.

The sync is **one-way** (vault → repo) with `--delete`. Anything in `notes/<slug>/` not present in the vault is removed. Empty Obsidian folders (no `.md` files) are skipped — their slugs don't appear in `_quarto.yml` or the sidebar.

#### What `make sync-notes` does

1. Iterates top-level subdirectories of `$OBSIDIAN_VAULT_NOTES`.
2. Slugifies each name (`01 - Terminal` → `01-terminal`).
3. rsyncs `*.md` files recursively from each vault folder into `notes/<slug>/`.
4. Removes any `notes/<slug>/` directories no longer present in the vault.
5. Regenerates the block between `# >>> auto-notes` and `# <<< auto-notes` in `_quarto.yml` — one `- auto: "notes/<slug>/"` entry per populated section, sorted alphabetically.

### Other sections

| Where | What |
|---|---|
| `projects/<slug>/index.md` | New project. Add an entry under `sidebar.id: projects` in `_quarto.yml`. |
| `blog/<post-name>.md` | New blog post. **No `_quarto.yml` edit needed** — the blog sidebar uses `contents: blog/` and auto-includes every `.md`. |

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
