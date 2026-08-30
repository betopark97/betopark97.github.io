# Diagrams

Quarto renders [Mermaid](https://mermaid.js.org/) and Graphviz diagrams natively, treating them as executable cells rather than code blocks.

## Fence syntax

The fence must use the braced form:

```` numberSource
```{mermaid}
graph LR
  A --> B
```
````

A plain ```` ```mermaid ```` fence is read as a code block in an unknown language and rendered as literal text. Most markdown editors that preview mermaid use the plain form, so a diagram authored elsewhere generally needs converting.

## File extension

A document containing an executable cell must use the `.qmd` extension. In a `.md` file the render aborts with:

``` numberSource
You must use the .qmd extension for documents with executable code
```

Both extensions produce the same output URL, so renaming a file to `.qmd` when a diagram is added does not change any links to it.

Graphviz uses `{dot}` and follows the same rules.

## Options

Cell options go in the fence body as `%%|` comments:

```` numberSource
```{mermaid}
%%| fig-width: 6
%%| label: fig-flow
%%| fig-cap: "A caption"
graph LR
  A --> B
```
````

`echo: false` suppresses the source, `fig-cap` adds a caption, and a `label` beginning `fig-` makes the diagram cross-referenceable as `@fig-flow`.

------------------------------------------------------------------------

Last modified: 2026-08-30

Back to top
