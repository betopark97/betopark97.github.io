# Visual Studio Code

## Workspace and folder configuration

Precedence is **workspace → folder → user**. A `.code-workspace` carries its own\
`"settings"` block, and it silently wins over user settings — including a stale\
absolute path that no longer exists. When a setting refuses to take effect, read\
the `.code-workspace` first.

### `${workspaceFolder}` is resolved by two different parties

- **VS Code** resolves it, but only in *workspace* settings. In user settings it\
  is passed through literally (`Could not resolve interpreter path '${workspaceFolder}/...'`). `python.defaultInterpreterPath` is one of these.
- **The extension** resolves it in its own code, in which case it works in user\
  settings too — `ruff.path` for example.

Nothing in the UI distinguishes them. Grep the bundle:

``` numberSource
grep -o 'workspaceFolder[^"]\{0,60\}' ~/.vscode/extensions/<ext>/dist/*.js | sort -u
```

Its own `value.replace("${workspaceFolder}", ...)` means it works anywhere.

### Multi-root resolves one value per window

`${workspaceFolder}` becomes **`folders[0]`** — the first entry in the\
`.code-workspace`, not the folder owning the file. Extensions often compound it\
by querying the workspace rather than the folder:

``` numberSource
api.settings.getExecutionDetails(workspace.workspaceFile)  // workspace-scoped
```

Symptom: **opening the folder directly works, opening it inside the multi-root\
workspace fails.** That asymmetry means per-folder `.vscode/settings.json` is\
never consulted, so the fix is one shared tool env pinned in the\
`.code-workspace`:

``` numberSource
uv venv ~/.venvs/<tool>
uv pip install --python ~/.venvs/<tool>/bin/python <tool>==<version>
```

Pin to the newest project in the window, and prefer this over borrowing a member\
repo’s `.venv`, which breaks when that repo is rebuilt.

## The editor runs a language server, not the CLI

`ruff check` and the ruff extension are different programs (`ruff server`), and\
they resolve config independently. Anything *inferred* can differ — so state\
tool config explicitly. A green CLI proves nothing about a squiggle.

Point tools at the project’s own binary rather than `PATH`, but only with a\
fallback — a hardcoded path that does not exist is worse than none:

``` numberSource
"ruff.importStrategy": "fromEnvironment"
```

## Finding what is drawing a squiggle

1.  **Problems panel** (`Cmd+Shift+M`) names the source extension. Hover does not,\
    if `editor.hover.enabled` is off.
2.  **What is actually installed** — the folder list lies, old versions linger:\
    `extensions.json` (registered) vs `.obsolete` (pending delete). In both =\
    mid-update, not uninstalled.
3.  **Live language servers** and their interpreter — catches a server on an old\
    Python where modern syntax is a parse error:\
    `ps aux | grep -i "language-server"`, then `lsof -a -p <pid> -d cwd -Fn`.
4.  **Logs** in `~/Library/Application Support/Code/logs/<session>/window*/exthost/`.\
    Many are empty; absence of a log is not absence of the problem.

## Related

- [uv](../../notes/001-terminal/003-uv.llms.md) for the venvs these settings point at

------------------------------------------------------------------------

Last modified: 2026-10-18

Back to top
