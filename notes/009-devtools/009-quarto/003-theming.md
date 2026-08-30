---
title: Theming
---
Quarto's HTML format builds on Bootstrap. `theme` selects a base theme, custom SCSS, or a list combining both.

```yaml
format:
  html:
    theme:
      - cosmo
      - custom.scss
      - later.scss
```

A bare name is one of the ~25 bundled [Bootswatch](https://bootswatch.com/) themes. A path ending in `.scss` is a custom file. Quarto compiles the whole list into a single stylesheet in one Sass pass, so no runtime CSS loading is involved.

## Order is the cascade

Files are applied in list order. A rule in a later file overrides an equally specific rule in an earlier one, and a variable default in a later file is only used if no earlier file set it. Splitting a theme into several files — palette, base rules, per-component rules — therefore means ordering them from most general to most specific.

To confirm what order a build actually used, search the compiled bundle in `_site/site_libs/bootstrap/` for a selector from each file and compare their positions.

## SCSS layers

A Quarto SCSS file is divided into layers by special comments. Each layer is spliced into a different point of the Bootstrap build:

```scss
/*-- scss:functions --*/
// helper functions, available to everything below

/*-- scss:defaults --*/
// Sass variable definitions, injected BEFORE Bootstrap's own defaults
$primary: #7287fd;
$body-bg: #1e1e2e;

/*-- scss:mixins --*/
// mixin definitions

/*-- scss:rules --*/
// plain CSS rules, appended AFTER Bootstrap
.custom-block { border-radius: 4px; }
```

The distinction that matters: variables belong in `scss:defaults` because Bootstrap's own variables are declared `!default` and only take effect if nothing set them first. A `$primary` written in `scss:rules` is too late to influence anything Bootstrap computed from it. Conversely a selector written in `scss:defaults` lands before Bootstrap and gets overridden by it.

A file may contain any subset of the layers, in any combination.

## Icons

Quarto bundles [Bootstrap Icons](https://icons.getbootstrap.com/) and loads the webfont on every page, so `<i class="bi bi-cloud"></i>` works with no setup. Config keys that accept an `icon` — navbar items, sidebar tools, callouts — take the name without the `bi-` prefix.

Any other icon set requires supplying the artwork, either as an inline SVG or as a file declared under `project.resources`.

## Scoping styles to a subset of pages

`body-classes` adds classes to `<body>`, so a rule can be written against a group of pages rather than all of them:

```yaml
body-classes: blog-post
```

Set it in a `_metadata.yml` to apply it to a whole directory, then key the SCSS off `.blog-post`.

***

[Last modified: 2026-08-30]{.note-modified}
