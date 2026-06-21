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

The full rules live in [conventions.md](conventions.md). In short:

- **Folders** (categories and subsections) are named `NNN-slug` — a 3-digit
  zero-padded number (sets sidebar/gallery order) + lowercase kebab-case slug,
  e.g. `001-terminal/`, `003-data-engineering/001-data-modeling/`.
- **Every folder has an `index.md`** with `title` (all folders), plus
  `description` and `icon` for top-level categories (these feed the gallery
  card). `icon:` is a [Bootstrap Icons](https://icons.getbootstrap.com/) name
  minus the `bi-` prefix (e.g. `icon: diagram-3`). Keep emoji out of `title`.
- **Files** are named `NNN-slug.md`; each note's `title:` frontmatter sets its
  sidebar label, independent of filename.
- The vault's **top-level `index.md`** body becomes the gallery's intro text.

`make sync-notes` validates all of this and reports anything that breaks the
rules (see below).

#### Sync command

```bash
make sync-notes
```

This **mirrors the vault and prints the convention report — it does not render.**
Read the report, fix any flagged files in Obsidian, re-run to re-check, then
`make preview` / `make render` to build.

The sync is **one-way** (vault → repo) with `--delete`. Anything in
`notes/<slug>/` not present in the vault is removed. Empty Obsidian folders (no
`.md` files) are skipped.

#### What `make sync-notes` does

1. `make clean` — busts Quarto's incremental cache so the next build picks up
   sidebar/title changes.
2. rsyncs `*.md` from each vault category into `notes/<slug>/`, and removes any
   `notes/<slug>/` no longer in the vault.
3. Regenerates the `# >>> auto-notes … # <<< auto-notes` block in `_quarto.yml`
   — one **scoped sidebar per category** (each with a "Notes" back-button, the
   section-name link, and the category's notes/subsections).
4. Regenerates the gallery shell `notes/index.md`: the `# >>> auto-contents`
   card list (one per category) and the `notes-intro` block (pulled from the
   vault's top-level `index.md`).
5. Prints the **convention report** (`--report`) — a dbt-style PASS/FAIL per
   folder/file plus a consolidated list of what to fix in Obsidian.

Build separately: `make preview` (live server) or `make render` (one-shot).
Both mirror first, then run Quarto — without the convention report.

### Other sections

| Where | What |
|---|---|
| `projects/<slug>/index.md` | New project. Add an entry under `sidebar.id: projects` in `_quarto.yml`. |
| `blog/<post-name>.md` | New blog post. **No `_quarto.yml` edit needed** — the blog sidebar uses `contents: blog/` and auto-includes every `.md`. |

### File-naming conventions

See [conventions.md](conventions.md) for the full Notes naming + metadata rules
(`NNN-slug` folders and files, required `index.md` frontmatter, where to get
`icon:` names). `make sync-notes` validates against them and reports violations.

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
