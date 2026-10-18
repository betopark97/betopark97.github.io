---
title: Quarto
description: "Publishing a website from markdown with Quarto: configuration, theming, navigation and filters."
icon: simple-icons:quarto
---
Quarto is a Pandoc-based publishing system. A project is a directory with a `_quarto.yml`; `quarto render` walks it, runs each input through Pandoc, and writes a site to an output directory.

These pages cover the parts of a `website` project: configuration, the Pandoc dialect and format options, SCSS theming, navigation, listings, Lua filters, diagrams, directory-level metadata, and publishing.

Current version: Quarto 1.9

## Reading Path

| Page | What it answers |
| --- | --- |
| [Project Config](001-project-config.md) | what `_quarto.yml` controls, and which files get rendered or copied |
| [Format and Dialect](002-format-and-dialect.md) | which markdown Pandoc accepts, and what `format: html` exposes |
| [Theming](003-theming.md) | how SCSS files layer into the Bootstrap build |
| [Navigation](004-navigation.md) | navbar, sidebars, and generating contents from a directory |
| [Listings](005-listings.md) | how a listing collects documents and renders them through a template |
| [Lua Filters](006-lua-filters.md) | how to transform the document AST, and when filters run |
| [Diagrams](007-diagrams.qmd) | why a mermaid block needs a specific fence and file extension |
| [Directory Metadata](008-directory-metadata.md) | how to apply frontmatter to every file in a folder |
| [Publishing](009-publishing.md) | render, preview, and deploying to GitHub Pages |
