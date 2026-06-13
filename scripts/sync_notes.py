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


def update_quarto_sidebar(slugs: list[str]) -> None:
    """Regenerate the auto-notes block in _quarto.yml with one explicit
    `auto:` entry per section, sorted alphabetically by slug. This pins the
    sidebar order to the numeric prefixes in folder names (01-, 02-, ...)
    rather than relying on Quarto's glob-expansion order, which sorts by
    directory mtime."""
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
        new_block.append(f'{indent}- auto: "notes/{slug}/"')
    new_block.append(lines[end])

    QUARTO_YML.write_text("\n".join(lines[:begin] + new_block + lines[end + 1 :]) + "\n")


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

    return 0


if __name__ == "__main__":
    sys.exit(main())
