#!/usr/bin/env python3
"""
One-way mirror from an Obsidian vault blog folder into ./blog/posts/.

Source of truth: Obsidian. Posts in blog/posts/ without a counterpart in the
vault are removed (so do not hand-author files inside blog/posts/ — author in
Obsidian and run this script). blog/index.md is the repo-authored listing
shell; only the prose between its intro markers is synced from the vault.

Vault layout
------------
  $OBSIDIAN_VAULT_BLOG/
    index.md          # optional intro prose (synced into blog/index.md)
    posts/
      <slug>.md       # one file per post

Frontmatter
-----------
Author Quarto-native field names in Obsidian; this script only translates the
one thing Obsidian models differently (`tags`) and normalises blanks:

  - REQUIRED: `title` + `date`. A post missing either is SKIPPED (never reaches
    Quarto, so the render can't fail) and reported by `--report`.
  - `tags` -> `categories` (block- or inline-style; each tag becomes a value).
  - empty OPTIONAL scalars (e.g. a blank `description:`/`image:`) are dropped,
    so a null value can't trip Quarto's schema.
  - everything else (`date`, `draft: true`, …) passes through verbatim.

Configuration
-------------
Required env var:
  OBSIDIAN_VAULT_BLOG   Path to the Blog folder inside the vault.
                        e.g. ~/Documents/MyVault/blog
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = REPO_ROOT / "blog"
POSTS_DIR = BLOG_DIR / "posts"
QUARTO_YML = REPO_ROOT / "_quarto.yml"

SIDEBAR_BEGIN = "# >>> auto-blog"
SIDEBAR_END = "# <<< auto-blog"

# Markers in blog/index.md (the hand-authored listing shell) bracketing the
# intro prose, which is sourced from the vault's Blog index.md.
INTRO_BEGIN = "<!-- >>> blog-intro"
INTRO_END = "<!-- <<< blog-intro -->"

# Fields a post must define to be published; anything else is optional and
# dropped when blank.
REQUIRED = ("title", "date")

# A post filename is a lowercase kebab-case slug + `.md` (no numeric prefix —
# blog posts order by date, not filename).
FILE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")

# Obsidian writes mermaid diagrams as ```mermaid fences; Quarto only treats the
# braced form ```{mermaid} as a diagram cell, and refuses to process diagram
# cells in a .md file at all. Posts containing a mermaid fence (either
# spelling) are normalised to the braced form and published as .qmd — same
# output .html, so URLs don't change.
MERMAID_FENCE_RE = re.compile(r"^```\{?mermaid\}?[ \t]*$", re.MULTILINE)

LIST_ITEM_RE = re.compile(r"\s+-\s+(.*)$")
KEY_RE = re.compile(r"([A-Za-z0-9_-]+):\s*(.*)$")

# Routine progress is only printed in verbose mode (set when `--report` is passed,
# i.e. `make sync-blog`). A bare `make preview` / `make render` stays quiet except
# for a one-line summary; genuine warnings/errors always print to stderr.
_VERBOSE = False


def log(msg: str) -> None:
    if _VERBOSE:
        print(msg, file=sys.stderr)


def frontmatter_bounds(lines: list[str]) -> tuple[int, int] | None:
    """Return (start, end) line indices of the `--- ... ---` frontmatter block,
    or None if absent."""
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return 0, i
    return None


def read_scalars(path: Path) -> dict[str, str]:
    """Top-level scalar keys from a file's frontmatter (a block list shows as an
    empty value, which is enough for the publish gate / required-field check)."""
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return {}
    bounds = frontmatter_bounds(lines)
    if bounds is None:
        return {}
    out: dict[str, str] = {}
    for ln in lines[bounds[0] + 1 : bounds[1]]:
        m = KEY_RE.match(ln)
        if m:
            out[m.group(1)] = m.group(2).strip().strip("\"'")
    return out


def translate(text: str) -> str:
    """Rewrite a post's frontmatter: `tags` -> `categories`, drop empty optional
    scalars, pass everything else through. See the module docstring."""
    lines = text.splitlines()
    bounds = frontmatter_bounds(lines)
    if bounds is None:
        return text
    start, end = bounds
    body = lines[start + 1 : end]

    out: list[str] = []
    categories: list[str] = []
    i = 0
    while i < len(body):
        m = KEY_RE.match(body[i])
        key = m.group(1) if m else None
        val = m.group(2).strip() if m else ""

        if key == "tags":
            if val:  # inline: `tags: [a, b]` or `tags: a`
                categories = [t.strip().strip("\"'") for t in val.strip("[]").split(",") if t.strip()]
                i += 1
            else:  # block: consume the indented `- item` lines below
                i += 1
                while i < len(body) and (li := LIST_ITEM_RE.match(body[i])):
                    categories.append(li.group(1).strip().strip("\"'"))
                    i += 1
            continue  # `tags` itself is dropped; `categories` is emitted below

        # Drop an empty scalar (e.g. blank `description:`/`image:`) so a null
        # value can't fail the render — but keep a block-list parent (its
        # indented items follow on the next line).
        if key and not val and not (i + 1 < len(body) and LIST_ITEM_RE.match(body[i + 1])):
            i += 1
            continue

        out.append(body[i])
        i += 1

    if categories:
        out.append("categories:")
        out.extend(f"  - {c}" for c in categories)

    new = lines[: start + 1] + out + lines[end:]
    return "\n".join(new) + ("\n" if text.endswith("\n") else "")


def strip_frontmatter(text: str) -> str:
    """Return `text` with a leading `--- ... ---` YAML frontmatter block removed."""
    lines = text.splitlines()
    bounds = frontmatter_bounds(lines)
    if bounds is None:
        return text.strip()
    return "\n".join(lines[bounds[1] + 1 :]).strip()


def check_dividers(path: Path) -> list[str]:
    """Flag bare `---` horizontal-rule dividers in the body that aren't fenced by
    blank lines (see docs/conventions.md). The leading frontmatter pair is
    exempt. A divider with no blank line after it makes Quarto parse the next
    lines as a second YAML block and the render dies."""
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return []
    bounds = frontmatter_bounds(lines)
    start = bounds[1] + 1 if bounds else 0
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


def sync_posts(posts_src: Path) -> list[tuple[str, str]]:
    """Translate every publishable post from the vault into blog/posts/, prune
    posts with no vault counterpart, and return (filename, date) pairs. A post
    missing a required field is skipped (never reaches Quarto)."""
    POSTS_DIR.mkdir(parents=True, exist_ok=True)

    synced: list[tuple[str, str]] = []
    for src in sorted(posts_src.iterdir()):
        if src.suffix != ".md" or src.name == "index.md" or src.name.startswith("."):
            continue
        fm = read_scalars(src)
        missing = [k for k in REQUIRED if not fm.get(k)]
        if missing:
            log(f"skipping blog/posts/{src.name} (missing required: {', '.join(missing)})")
            continue
        text = translate(src.read_text())
        out_name = src.name
        if MERMAID_FENCE_RE.search(text):
            text = MERMAID_FENCE_RE.sub("```{mermaid}", text)
            out_name = src.stem + ".qmd"
        (POSTS_DIR / out_name).write_text(text)
        log(f"syncing {src.name} → blog/posts/{out_name}")
        synced.append((out_name, fm["date"]))

    expected = {name for name, _ in synced}
    for existing in POSTS_DIR.iterdir():
        if existing.suffix in (".md", ".qmd") and existing.name not in expected:
            log(f"removing stale post: blog/posts/{existing.name}")
            existing.unlink()

    return synced


def update_quarto_sidebar(posts: list[tuple[str, str]]) -> None:
    """Regenerate the auto-blog block in _quarto.yml: the blog landing first,
    then every post newest-first (by date) to match the listing order — pinning
    the sequence rather than leaving it to Quarto's FS traversal."""
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
    block = [
        lines[begin],
        f"{indent}- id: blog",
        f'{indent}  title: "Blog"',
        f"{indent}  contents:",
        f'{indent}    - text: "Blog"',
        f"{indent}      href: blog/index.md",
    ]
    for name, _ in sorted(posts, key=lambda p: p[1], reverse=True):
        block.append(f"{indent}    - blog/posts/{name}")
    block.append(lines[end])

    QUARTO_YML.write_text("\n".join(lines[:begin] + block + lines[end + 1 :]) + "\n")
    log("regenerated blog sidebar")


def update_blog_intro(src_root: Path) -> None:
    """Sync the listing page's intro prose from the vault's Blog index.md into the
    marked block of blog/index.md, leaving the listing frontmatter and tabset
    untouched (only the text between the INTRO markers is replaced). The intro is
    optional — an empty vault index.md just leaves the block empty."""
    index = BLOG_DIR / "index.md"
    src_index = src_root / "index.md"
    if not index.exists():
        return
    if not src_index.is_file():
        print("no index.md at the Blog root in the vault; leaving intro as-is", file=sys.stderr)
        return

    text = index.read_text()
    begin = text.find(INTRO_BEGIN)
    end = text.find(INTRO_END)
    if begin == -1 or end == -1:
        print(
            f"warning: intro markers not found in blog/index.md; "
            f"expected '{INTRO_BEGIN}' / '{INTRO_END}' — skipping intro update",
            file=sys.stderr,
        )
        return

    after_begin = text.index("\n", begin) + 1  # keep the begin-marker line
    body = strip_frontmatter(src_index.read_text())
    middle = (body + "\n") if body else ""
    index.write_text(text[:after_begin] + middle + text[end:])
    log("synced blog intro from vault Blog index.md")


def validate_vault(posts_src: Path) -> list:
    """Walk the vault posts and collect convention issues per post (filename,
    required fields, dividers)."""
    results: list = []
    for src in sorted(posts_src.iterdir()):
        if src.suffix != ".md" or src.name == "index.md" or src.name.startswith("."):
            continue
        fm = read_scalars(src)
        issues: list[str] = []
        if not FILE_RE.match(src.name):
            issues.append("filename must be lowercase kebab-case (slug.md, no numeric prefix)")
        for k in REQUIRED:
            if not fm.get(k):
                issues.append(f"missing required '{k}' — post is skipped until set")
        title = fm.get("title", "")
        if title and any(ord(c) > 127 for c in title):
            issues.append("'title' contains non-ASCII (emoji?) — keep titles plain")
        issues.extend(check_dividers(src))
        results.append((src.name, issues))
    return results


def print_validation_report(results: list) -> None:
    """dbt-style PASS/FAIL per item, then a consolidated fix-list of failures."""
    tty = sys.stdout.isatty()
    def paint(code: str, s: str) -> str:
        return f"\033[{code}m{s}\033[0m" if tty else s
    ok, bad = paint("32", "PASS"), paint("31", "FAIL")

    print("\n" + "─" * 64)
    print("Convention check (vault blog) — see docs/conventions.md")
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
    global _VERBOSE
    _VERBOSE = "--report" in sys.argv

    vault = os.environ.get("OBSIDIAN_VAULT_BLOG")
    if not vault:
        print(
            "OBSIDIAN_VAULT_BLOG is not set. Add it to .env pointing at the Blog "
            "folder in your Obsidian vault. The Makefile auto-loads .env before "
            "running sync targets.",
            file=sys.stderr,
        )
        return 1

    src_root = Path(vault).expanduser().resolve()
    if not src_root.is_dir():
        print(f"OBSIDIAN_VAULT_BLOG does not point to a directory: {src_root}", file=sys.stderr)
        return 1

    posts_src = src_root / "posts"
    if not posts_src.is_dir():
        print(f"no posts/ folder in the vault blog at {posts_src}", file=sys.stderr)
        return 1

    BLOG_DIR.mkdir(exist_ok=True)

    total = sum(1 for p in posts_src.iterdir() if p.suffix == ".md" and p.name != "index.md")
    posts = sync_posts(posts_src)
    update_quarto_sidebar(posts)
    update_blog_intro(src_root)

    suffix = "" if _VERBOSE else " — run `make sync-blog` for details"
    print(f"blog: synced {len(posts)} post(s), skipped {total - len(posts)}{suffix}")

    # The convention check is opt-in (--report) so it only prints for
    # `make sync-blog`, not on every `make preview` / `make render`.
    if _VERBOSE:
        print_validation_report(validate_vault(posts_src))

    return 0


if __name__ == "__main__":
    sys.exit(main())
