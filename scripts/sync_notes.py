#!/usr/bin/env python3
"""
One-way mirror from an Obsidian vault folder into ./notes/.

Source of truth: Obsidian. Anything in notes/ that does not have a
counterpart in the vault is removed (so do not hand-author files inside
notes/ — author in Obsidian and run this script).

Layout convention
-----------------
Vault folder names like "01 - Terminal/" are slugified to "01-terminal/"
so Quarto's `auto:` sidebar lists sections in the intended numeric order.
A stub index.md is generated per section with a `title:` frontmatter
stripping the numeric prefix, so the sidebar header reads "Terminal"
instead of "01 - Terminal".

Configuration
-------------
Required env var:
  OBSIDIAN_VAULT_NOTES   Path to the Notes folder inside the vault.
                         e.g. ~/Documents/MyVault/Notes
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
NOTES_DIR = REPO_ROOT / "notes"
QUARTO_YML = REPO_ROOT / "_quarto.yml"

SIDEBAR_BEGIN = "# >>> auto-notes"
SIDEBAR_END = "# <<< auto-notes"

# Markers in notes/index.md (the hand-authored gallery shell) bracketing the
# intro prose, which is sourced from the vault's Notes index.md.
INTRO_BEGIN = "<!-- >>> notes-intro"
INTRO_END = "<!-- <<< notes-intro -->"

# Markers inside the gallery's listing `contents:` (YAML comments), bracketing
# the per-category entries, which are regenerated from the synced categories.
CONTENTS_BEGIN = "# >>> auto-contents"
CONTENTS_END = "# <<< auto-contents"

# Naming convention (see docs/conventions.md): a 3-digit zero-padded number
# prefix + lowercase kebab-case slug. Folders use it bare; files add `.md`.
FOLDER_RE = re.compile(r"^\d{3}-[a-z0-9]+(?:-[a-z0-9]+)*$")
FILE_RE = re.compile(r"^\d{3}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")


def slugify(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")


def has_md(directory: Path) -> bool:
    return any(directory.rglob("*.md"))


def rsync_md(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "rsync", "-a", "--delete",
            "--include=*/", "--include=*.md", "--exclude=*",
            f"{src}/", f"{dst}/",
        ],
        check=True,
    )


def section_title(slug: str) -> str:
    """Read the `title:` from notes/<slug>/index.md frontmatter so the sidebar
    header matches the page's own title. Falls back to a prettified slug
    (numeric prefix stripped, title-cased) if the file or field is missing."""
    index = NOTES_DIR / slug / "index.md"
    try:
        lines = index.read_text().splitlines()
    except OSError:
        lines = []
    if lines and lines[0].strip() == "---":
        for ln in lines[1:]:
            if ln.strip() == "---":
                break
            m = re.match(r"\s*title:\s*(.+)", ln)
            if m:
                return m.group(1).strip().strip("\"'")
    return re.sub(r"^\d+-", "", slug).replace("-", " ").title()


def section_entries(slug: str, indent: str) -> list[str]:
    """Build a self-contained sidebar object for one section, so each top-level
    category renders its OWN scoped sidebar (you only ever see the tree for the
    category you're in, never all of them). The category's index page is bound
    via an explicit link labelled with the section name — a bare
    `auto: "notes/<slug>/"` lets Quarto
    decide how to render the node, and that choice is inconsistent (a folder with
    index.md + a single note becomes a collapse-only section with no link, so
    visiting its index shows no sidebar at all). Subdirs are listed via nested
    `auto:` and loose `.md` files explicitly, so order is pinned by slug rather
    than Quarto's FS-entry-order traversal (effectively random on APFS)."""
    section_dir = NOTES_DIR / slug
    children = sorted(section_dir.iterdir(), key=lambda p: p.name)
    title = section_title(slug)

    # First entry links the category's index page, labelled with the section
    # name (e.g. "Terminal") rather than a generic "Overview".
    contents = [
        f'{indent}    - text: "{title}"',
        f"{indent}      href: notes/{slug}/index.md",
    ]
    for child in children:
        if child.name == "index.md":
            continue
        if child.is_dir():
            contents.append(f'{indent}    - auto: "notes/{slug}/{child.name}/"')
        elif child.suffix == ".md":
            contents.append(f"{indent}    - notes/{slug}/{child.name}")

    # A back-to-gallery affordance via Quarto's built-in sidebar `tools` (an
    # internal link, so it works in preview and deployed). Tools live outside
    # `contents`, so — unlike a contents link — Quarto leaves them out of the
    # bottom prev/next sequence automatically; no CSS hack needed. It renders
    # as a back-arrow icon, labelled "Notes" via CSS (styles.scss).
    return [
        f"{indent}- id: notes-{slug}",
        f'{indent}  title: "{title}"',
        f"{indent}  tools:",
        f"{indent}    - icon: arrow-left-circle",
        f"{indent}      text: Notes",
        f"{indent}      href: notes/index.md",
        f"{indent}  contents:",
        *contents,
    ]


def update_quarto_sidebar(slugs: list[str]) -> None:
    """Regenerate the auto-notes block in _quarto.yml. Emits one scoped
    sidebar object per category (sorted by slug) directly into the top-level
    `sidebar:` list, so each category page shows only its own tree. The notes
    landing (`notes/index.md`) is deliberately left out of every sidebar so it
    renders full-width as the gallery entry point."""
    lines = QUARTO_YML.read_text().splitlines()
    begin = next((i for i, ln in enumerate(lines) if SIDEBAR_BEGIN in ln), None)
    end = next((i for i, ln in enumerate(lines) if SIDEBAR_END in ln), None)
    if begin is None or end is None:
        print(
            f"warning: markers not found in {QUARTO_YML.name}; "
            f"expected '{SIDEBAR_BEGIN}' / '{SIDEBAR_END}' — skipping sidebar update",
            file=sys.stderr,
        )
        return

    indent = lines[begin][: len(lines[begin]) - len(lines[begin].lstrip())]
    new_block = [lines[begin]]
    for slug in sorted(slugs):
        new_block.extend(section_entries(slug, indent))
    new_block.append(lines[end])

    QUARTO_YML.write_text("\n".join(lines[:begin] + new_block + lines[end + 1 :]) + "\n")


def strip_frontmatter(text: str) -> str:
    """Return `text` with a leading `--- ... ---` YAML frontmatter block removed."""
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1 :]).strip()
    return text.strip()


def update_gallery_intro(src_root: Path) -> None:
    """Sync the gallery's intro prose from the vault's Notes index.md into the
    marked block of notes/index.md. The gallery's frontmatter (listing config)
    and the `::: {#notes-categories}` placeholder are left untouched — only the
    text between the INTRO markers is replaced, so the prose is authored in
    Obsidian while the listing machinery stays in the repo."""
    gallery = NOTES_DIR / "index.md"
    src_index = src_root / "index.md"
    if not gallery.exists():
        return
    if not src_index.is_file():
        print(
            "no index.md at the Notes root in the vault; leaving gallery intro as-is",
            file=sys.stderr,
        )
        return

    text = gallery.read_text()
    begin = text.find(INTRO_BEGIN)
    end = text.find(INTRO_END)
    if begin == -1 or end == -1:
        print(
            f"warning: intro markers not found in notes/index.md; "
            f"expected '{INTRO_BEGIN}' / '{INTRO_END}' — skipping intro update",
            file=sys.stderr,
        )
        return

    after_begin = text.index("\n", begin) + 1  # keep the begin-marker line
    body = strip_frontmatter(src_index.read_text())
    new = text[:after_begin] + body + "\n" + text[end:]
    gallery.write_text(new)
    print("synced gallery intro from vault Notes index.md")


def update_gallery_contents(slugs: list[str]) -> None:
    """Regenerate the listing `contents:` in notes/index.md from the synced
    category slugs (sorted), so adding or removing a category in the vault
    updates the gallery cards automatically — mirroring the sidebar block in
    _quarto.yml. Each entry is the category's index page, relative to the
    gallery (e.g. `001-terminal/index.md`)."""
    gallery = NOTES_DIR / "index.md"
    if not gallery.exists():
        return
    lines = gallery.read_text().splitlines()
    begin = next((i for i, ln in enumerate(lines) if CONTENTS_BEGIN in ln), None)
    end = next((i for i, ln in enumerate(lines) if CONTENTS_END in ln), None)
    if begin is None or end is None:
        print(
            f"warning: contents markers not found in notes/index.md; "
            f"expected '{CONTENTS_BEGIN}' / '{CONTENTS_END}' — skipping",
            file=sys.stderr,
        )
        return

    indent = lines[begin][: len(lines[begin]) - len(lines[begin].lstrip())]
    new_block = [lines[begin]]
    new_block += [f"{indent}- {slug}/index.md" for slug in sorted(slugs)]
    new_block.append(lines[end])
    gallery.write_text("\n".join(lines[:begin] + new_block + lines[end + 1 :]) + "\n")
    print("regenerated gallery listing contents")


def read_frontmatter(path: Path) -> dict[str, str]:
    """Best-effort parse of top-level scalar keys from a file's YAML frontmatter."""
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return {}
    if not lines or lines[0].strip() != "---":
        return {}
    out: dict[str, str] = {}
    for ln in lines[1:]:
        if ln.strip() == "---":
            break
        m = re.match(r"([A-Za-z0-9_-]+):\s*(.*)$", ln)
        if m:
            out[m.group(1)] = m.group(2).strip().strip("\"'")
    return out


def check_dividers(path: Path) -> list[str]:
    """Flag bare `---` horizontal-rule dividers in the body that aren't fenced by
    blank lines (see docs/conventions.md §5). The leading frontmatter `---`/`---`
    pair is exempt — that's the metadata block. A divider with no blank line
    *after* it makes Quarto parse the following prose as a second YAML block and
    the render dies; no blank line *before* it turns the previous line into a
    heading."""
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return []
    # Skip the leading frontmatter so its fences aren't mistaken for dividers.
    start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start = i + 1
                break
    issues: list[str] = []
    for i in range(start, len(lines)):
        if lines[i].strip() != "---":
            continue
        after_blank = i + 1 >= len(lines) or lines[i + 1].strip() == ""
        before_blank = i == 0 or lines[i - 1].strip() == ""
        if not after_blank:
            issues.append(
                f"line {i + 1}: '---' divider needs a blank line after it, else "
                f"Quarto parses the next lines as YAML and the render fails "
                f"(add a blank line, or use '***')"
            )
        elif not before_blank:
            issues.append(
                f"line {i + 1}: '---' divider needs a blank line before it, else "
                f"the previous line becomes a heading (add a blank line, or use '***')"
            )
    return issues


def _check_folder(folder: Path, src_root: Path, top_level: bool, results: list) -> None:
    """Validate one folder, its index.md, and (recursively) its children against
    the project conventions, appending (relative_path, [issues]) tuples."""
    rel = folder.relative_to(src_root)

    folder_issues: list[str] = []
    if not FOLDER_RE.match(folder.name):
        folder_issues.append("folder name must be NNN-slug (3-digit number + lowercase kebab-case)")
    index = folder / "index.md"
    if not index.is_file():
        folder_issues.append("missing index.md")
    results.append((f"{rel}/", folder_issues))

    if index.is_file():
        fm = read_frontmatter(index)
        index_issues: list[str] = []
        title = fm.get("title", "")
        if not title:
            index_issues.append("missing 'title'")
        elif any(ord(c) > 127 for c in title):
            index_issues.append("'title' contains non-ASCII (emoji?) — keep titles plain; use 'icon:'")
        if top_level and not fm.get("description"):
            index_issues.append("missing 'description' (feeds the gallery card)")
        if top_level and not fm.get("icon"):
            index_issues.append("missing 'icon' (Bootstrap icon name; see docs/conventions.md)")
        index_issues.extend(check_dividers(index))
        results.append((f"{rel}/index.md", index_issues))

    for child in sorted(folder.iterdir(), key=lambda p: p.name):
        if child.name.startswith("."):
            continue
        if child.is_dir():
            _check_folder(child, src_root, False, results)
        elif child.suffix == ".md" and child.name != "index.md":
            file_issues: list[str] = []
            if not FILE_RE.match(child.name):
                file_issues.append("filename must be NNN-slug.md (3-digit number + lowercase kebab-case)")
            if not read_frontmatter(child).get("title"):
                file_issues.append("missing 'title'")
            file_issues.extend(check_dividers(child))
            results.append((str(rel / child.name), file_issues))


def validate_vault(src_root: Path) -> list:
    """Walk the vault and collect convention issues per folder/file."""
    results: list = []
    root_index = src_root / "index.md"
    if not root_index.is_file():
        results.append(("index.md", ["missing Notes root index.md (the gallery intro source)"]))
    else:
        results.append(("index.md", check_dividers(root_index)))
    for cat in sorted(p for p in src_root.iterdir() if p.is_dir() and not p.name.startswith(".")):
        _check_folder(cat, src_root, True, results)
    return results


def print_validation_report(results: list) -> None:
    """dbt-style PASS/FAIL per item, then a consolidated fix-list of failures."""
    tty = sys.stdout.isatty()
    def paint(code: str, s: str) -> str:
        return f"\033[{code}m{s}\033[0m" if tty else s
    ok, bad = paint("32", "PASS"), paint("31", "FAIL")

    print("\n" + "─" * 64)
    print("Convention check (vault) — see docs/conventions.md")
    print("─" * 64)
    for path, issues in results:
        if issues:
            print(f"  {bad}  {path}")
            for i in issues:
                print(f"          - {i}")
        else:
            print(f"  {ok}  {path}")

    failed = [(p, i) for p, i in results if i]
    passed = len(results) - len(failed)
    print("─" * 64)
    print(f"Done. {len(results)} checked  |  "
          f"{paint('32', f'{passed} passed')}  |  {paint('31', f'{len(failed)} failed')}")

    if failed:
        print("\n" + paint("1", "Fix these in your Obsidian vault:"))
        for path, issues in failed:
            print(f"  {paint('31', '✗')} {path}")
            for i in issues:
                print(f"      - {i}")
    print()


def main() -> int:
    vault = os.environ.get("OBSIDIAN_VAULT_NOTES")
    if not vault:
        print(
            "OBSIDIAN_VAULT_NOTES is not set. Copy .env.example to .env and "
            "edit the path to point at the Notes folder in your Obsidian "
            "vault. The Makefile auto-loads .env before running sync targets.",
            file=sys.stderr,
        )
        return 1

    src_root = Path(vault).expanduser().resolve()
    if not src_root.is_dir():
        print(
            f"OBSIDIAN_VAULT_NOTES does not point to a directory: {src_root}",
            file=sys.stderr,
        )
        return 1

    NOTES_DIR.mkdir(exist_ok=True)

    # Only sections that contain at least one .md anywhere in their tree
    # make it into the repo. Empty Obsidian folders are skipped silently —
    # Quarto's `auto:` errors on empty directories, and there's nothing
    # useful to show in the sidebar for them anyway.
    pairs: list[tuple[Path, str]] = []
    for child in sorted(src_root.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        if not has_md(child):
            continue
        pairs.append((child, slugify(child.name)))

    expected = {slug for _, slug in pairs}

    for existing in NOTES_DIR.iterdir():
        if not existing.is_dir() or existing.name in expected:
            continue
        print(f"removing stale section: notes/{existing.name}/")
        shutil.rmtree(existing)

    for src_dir, slug in pairs:
        dst_dir = NOTES_DIR / slug
        print(f"syncing {src_dir.name} → notes/{slug}/")
        rsync_md(src_dir, dst_dir)

    update_quarto_sidebar([slug for _, slug in pairs])
    update_gallery_contents([slug for _, slug in pairs])
    update_gallery_intro(src_root)

    # The convention check is opt-in (--report) so it only prints for
    # `make sync-notes`, not on every `make preview` / `make render`.
    if "--report" in sys.argv:
        print_validation_report(validate_vault(src_root))

    return 0


if __name__ == "__main__":
    sys.exit(main())
