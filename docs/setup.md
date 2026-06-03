# Setup

Steps to set up this Quarto site from scratch, or onboard a new contributor.

## Prerequisites

- [Quarto](https://quarto.org/docs/get-started/) (≥ 1.4)
- Git
- (Optional) [GitHub CLI](https://cli.github.com/) for managing the repo from the terminal
- A GitHub repo named `<username>.github.io` if deploying as a user site

## 1. Clone the repo

```bash
git clone git@github.com:betopark97/betopark97.github.io.git
cd betopark97.github.io
```

## 2. Project layout

```
_quarto.yml              # Site config: navbar, sidebars, theme
index.qmd                # Portfolio (homepage)
manual/                  # Data Analysis Manual chapters
projects/                # Projects gallery + individual projects
blog/                    # Blog posts (currently stub)
study/                   # Study notes (currently stub)
custom_header.html       # GA + meta tags injected into <head>
custom_body.html         # HTML injected before </body>
styles.css               # Custom CSS (currently empty)
img/, data/              # Static assets
docs/                    # This documentation (not rendered into the site)
_site/                   # Rendered output (gitignored)
.github/workflows/       # CI: publish.yml builds and deploys
```

## 3. Local preview

```bash
quarto preview
```

Opens a live-reloading dev server. Edit any `.qmd`, save, and the browser refreshes.

## 4. One-time GitHub Pages config

If you're bootstrapping a fresh deployment:

1. From any branch, run:
   ```bash
   quarto publish gh-pages
   ```
   This creates the `gh-pages` branch on the remote, pushes the built site to it, and writes a `_publish.yml` file. Commit `_publish.yml`.

2. In the repo's GitHub Settings → Pages, set:
   - **Source**: *Deploy from a branch*
   - **Branch**: `gh-pages`
   - **Folder**: `/(root)`

After that, CI handles every subsequent deploy — no more manual `quarto publish`.

## 5. CI workflow

`.github/workflows/publish.yml` runs on every push to `main`:

1. Checks out the repo
2. Installs Quarto
3. Runs `quarto render` → `_site/`
4. Pushes the rendered files to the `gh-pages` branch
5. GitHub Pages serves `gh-pages` at https://betopark97.github.io/

## Things to note

- **`.md` vs `.qmd`**: the `render: "*.qmd"` line in `_quarto.yml` means only `.qmd` files are rendered into the site. Files like this one stay out of the deployed site. Use `.md` for repo-internal docs, `.qmd` for site content.
- **Don't commit `_site/`** — it's gitignored. CI rebuilds it from source.
- **`docs/` used to be the output directory** (when `output-dir: docs`); it's now repurposed for repo documentation.
