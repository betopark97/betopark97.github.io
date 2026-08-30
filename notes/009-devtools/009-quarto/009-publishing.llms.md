# Publishing

## Local

| Command          | Effect                                                   |
|------------------|----------------------------------------------------------|
| `quarto render`  | build the project once into `output-dir` and exit        |
| `quarto preview` | build, serve on localhost, watch for changes and rebuild |
| `quarto check`   | environment diagnostics — versions, Pandoc, engines      |

`preview` is `render` plus a dev server and file watcher; the output is identical. Both accept a single file path to limit work to one document.

Renders are incremental. Deleting `output-dir` and the `.quarto/` cache forces a full rebuild, which is what is needed when the change is in an included file that Quarto does not track as a dependency.

## GitHub Pages

`quarto publish gh-pages` renders and pushes the result to a `gh-pages` branch. The branch is machine-generated and should never be edited by hand.

In CI, the same thing is done with the official actions:

``` numberSource
- uses: quarto-dev/quarto-actions/setup@v2

- uses: quarto-dev/quarto-actions/publish@v2
  with:
    target: gh-pages
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

The job needs `permissions: contents: write` to push the branch. `setup@v2` accepts a `version` input to pin Quarto; without it the latest release is installed, so a render that passes locally can fail in CI on a version difference.

Other `target` values are `netlify`, `posit-connect`, `confluence`, and `quarto-pub`.

## Deploying only when something changed

Because `render` is the expensive step, a scheduled workflow can compare the current inputs against what is already deployed and skip the render when they match — fetch the deployed copy of the generated file, diff it against a freshly generated one, and gate the remaining steps on the result. This keeps a daily refresh job cheap when most runs are no-ops.

------------------------------------------------------------------------

Last modified: 2026-08-30

Back to top
