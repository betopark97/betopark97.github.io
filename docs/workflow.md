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

| Where | What |
|---|---|
| `manual/chapterN.qmd` | New chapter. Add a `- text: ... / href: ...` entry under `sidebar.id: manual` in `_quarto.yml`. |
| `projects/<slug>/index.qmd` | New project. Add an entry under `sidebar.id: projects`. |
| `blog/<post-name>.qmd` | New blog post. **No `_quarto.yml` edit needed** — the blog sidebar uses `contents: blog/` and auto-includes every `.qmd`. |
| `study/<page>.qmd` | Same auto-include behavior as `blog/`. |

## Common tweaks

- **Theme**: `_quarto.yml` → `format.html.theme` (currently `cosmos` light / `darkly` dark).
- **Navbar items / order**: `website.navbar.left`.
- **Footer**: `website.page-footer`.
- **Analytics / meta tags**: `custom_header.html`.

## Troubleshooting

- **CI fails on render**: open the Actions tab on GitHub and read the log. Usually broken `.qmd` syntax, a missing image path, or a typo in `_quarto.yml`.
- **Pages serves wrong content**: re-check Settings → Pages still points to `gh-pages` / `/(root)`.
- **Local render works, CI fails**: typically a case-sensitivity issue. macOS is case-insensitive; the Linux runner isn't. Check the exact casing of every filename referenced in `href:` paths.
- **Stale browser**: hard-refresh (Cmd+Shift+R) — GitHub Pages aggressively caches.
