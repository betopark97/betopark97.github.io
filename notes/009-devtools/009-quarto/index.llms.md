# Quarto

Quarto is a Pandoc-based publishing system. A project is a directory with a `_quarto.yml`; `quarto render` walks it, runs each input through Pandoc, and writes a site to an output directory.

These pages cover the parts of a `website` project: configuration, the Pandoc dialect and format options, SCSS theming, navigation, listings, Lua filters, diagrams, directory-level metadata, and publishing.

Current version: Quarto 1.9

## Reading Path

| Page | What it answers |
|----|----|
| [Project Config](../../../notes/009-devtools/009-quarto/001-project-config.llms.md) | what `_quarto.yml` controls, and which files get rendered or copied |
| [Format and Dialect](../../../notes/009-devtools/009-quarto/002-format-and-dialect.llms.md) | which markdown Pandoc accepts, and what `format: html` exposes |
| [Theming](../../../notes/009-devtools/009-quarto/003-theming.llms.md) | how SCSS files layer into the Bootstrap build |
| [Navigation](../../../notes/009-devtools/009-quarto/004-navigation.llms.md) | navbar, sidebars, and generating contents from a directory |
| [Listings](../../../notes/009-devtools/009-quarto/005-listings.llms.md) | how a listing collects documents and renders them through a template |
| [Lua Filters](../../../notes/009-devtools/009-quarto/006-lua-filters.llms.md) | how to transform the document AST, and when filters run |
| [Diagrams](../../../notes/009-devtools/009-quarto/007-diagrams.llms.md) | why a mermaid block needs a specific fence and file extension |
| [Directory Metadata](../../../notes/009-devtools/009-quarto/008-directory-metadata.llms.md) | how to apply frontmatter to every file in a folder |
| [Publishing](../../../notes/009-devtools/009-quarto/009-publishing.llms.md) | render, preview, and deploying to GitHub Pages |

Back to top
