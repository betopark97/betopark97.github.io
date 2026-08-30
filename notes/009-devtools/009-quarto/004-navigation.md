---
title: Navigation
---
A `website` project reads a `website:` block for site-level chrome.

```yaml
website:
  title: "Site title"
  favicon: assets/favicon.svg
  page-navigation: true
  back-to-top-navigation: true
```

`page-navigation` adds previous/next links at the foot of each page, ordered by the sidebar. `llms-txt: true` emits an `llms.txt` index plus a plain-markdown `.llms.md` alongside each page.

## Navbar

```yaml
website:
  navbar:
    title: "Displayed name"
    background: light
    search: true
    left:
      - icon: github
        href: https://github.com/org/repo
    right:
      - href: index.md
        text: Home
      - href: notes/index.md
        text: Notes
```

Items go in `left`, `center`, or `right`. Each is `text` + `href`, `icon` + `href`, or a `menu` of nested items. An `href` pointing at a source file is rewritten to the rendered URL.

## Sidebars

A site can define several sidebars. Each gets an `id`, and Quarto shows the one whose `contents` include the current page:

```yaml
website:
  sidebar:
    - id: notes
      title: "Notes"
      collapse-level: 1
      tools:
        - icon: arrow-left-circle
          text: Back
          href: notes/index.md
      contents:
        - text: "Overview"
          href: notes/index.md
        - notes/topic/001-first.md
        - auto: "notes/other-topic/"
```

| Key | Effect |
| --- | --- |
| `id` | identifies the sidebar; a page appearing in its `contents` selects it |
| `contents` | entries: a bare path, a `text`/`href` pair, a `section` with nested `contents`, or `auto` |
| `collapse-level` | depth at which sections start collapsed |
| `tools` | icon links pinned above the contents |
| `style` | `floating` or `docked` |

`auto:` takes a glob or directory and generates entries from what is on disk, ordered by filename. A directory's `index.md` becomes the section landing page, and each entry's label comes from that file's `title` frontmatter, not its filename. Numbering filenames is the usual way to control order, since sorting is lexicographic — zero-pad so `010` does not sort before `002`.

Mixing explicit entries and `auto:` in one `contents` list is allowed, which is what makes a generated sidebar possible while keeping a hand-written entry at the top.

***

[Last modified: 2026-08-30]{.note-modified}
