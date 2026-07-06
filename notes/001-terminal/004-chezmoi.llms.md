# Chezmoi

## Intro

Chezmoi is a dotfiles manager that keeps your configuration files (`.zshrc`, `.gitconfig`, kitty config, etc.) in a single git repository and syncs them across machines. Instead of manually copying config files to a new machine or symlinking them one by one, you keep a source repo and let chezmoi write the files into `$HOME` for you.

## Mental Model

There are two trees to keep in mind:

- **Source**: the git repository where your dotfiles live, `chezmoi` repo. This is what you commit and push.
- **Target**: `$HOME`. This is what chezmoi writes out.

The flow to push and pull your files:

- `chezmoi apply` pushes source → target
- `chezmoi add|re-add` pulls target → source

``` mermaid
graph LR
    B["Target<br>$HOME"]
    A["Source<br>~/path/to/your/chezmoi"]
    A -->|chezmoi apply| B
    B -->|chezmoi add #124; re-add| A
```

## Installation

``` numberSource
brew install chezmoi
```

## Setup

By default chezmoi looks for source files in `~/.local/share/chezmoi`. If you want to keep your dotfiles repo somewhere else (e.g. alongside your other projects), you need to tell chezmoi where to look.

Create `~/.config/chezmoi/chezmoi.toml`, substituting your actual path:

``` numberSource
sourceDir = "~/path/to/your/chezmoi"
```

> **NOTE:**
>
> Should we save the `chezmoi.toml` file?
>
> ***Chicken-and-egg problem***  
> This config file can itself be tracked by the repo (at `dot_config/chezmoi/chezmoi.toml`), but you still have to create it by hand the first time, because chezmoi has to read it before it knows where the source directory is. After the initial `chezmoi apply`, chezmoi takes over and any future edits go through the source tree like everything else. However, I wouldn’t personally recommend it.

Verify it’s wired up:

``` numberSource
chezmoi source-path
# → /path/to/your/chezmoi
```

Then preview and apply. Always diff before applying on a new machine as the source tree may contain files that would overwrite something already in `$HOME`:

``` numberSource
chezmoi diff      # show changes against $HOME
chezmoi apply     # write to $HOME (overwrite)
```

> **WARNING:**
>
> Chezmoi tries to apply **everything** in the source tree to `$HOME`, not just files prefixed with `dot_`. Anything that isn’t a dotfile source (e.g. `README.md`, `docs/`) will be copied into `$HOME` verbatim unless it’s listed in `.chezmoiignore`. When adding non-dotfile content to the repo, add it to `.chezmoiignore`, and sanity-check with `chezmoi managed`.

## Workflow

### Common commands

``` numberSource
chezmoi cd                # drop into the source dir (the repo)
chezmoi diff              # show what apply would change in $HOME
chezmoi apply             # write chezmoi → $HOME
chezmoi add ~/.file       # start tracking a file (copy $HOME → chezmoi)
chezmoi re-add ~/.file    # pull edits made in $HOME back into chezmoi
chezmoi status            # short status of pending changes
chezmoi managed           # list every file chezmoi manages
```

### Adding a new dotfile

To start tracking a file that currently only lives in `$HOME`:

``` numberSource
chezmoi add ~/.some-config
```

Chezmoi copies it into the source tree, renaming it to its internal convention (e.g. `.some-config` → `dot_some-config`). Commit the new file from inside the repo.

### Editing a tracked file

The recommended way to edit the tracked file is to edit the source by doing `chezmoi edit ~/.some-config`. However, I prefer to just edit the live file as I don’t want to change the way I used to manage my files before chezmoi. Also, some configurations are changed automatically by tools (e.g. a binary setting paths to a zsh script) and the chezmoi recommended way can add overhead (e.g. changing a config in the native settings panel of an editor like VS Code or Obsidian but having to go to chezmoi to change it instead of inside the editor).

That’s why I just edit my tracked files manually in my editor of choice, VS Code, if it’s a file that can be opened and edited.

Then follow the steps:

1.  Re-add the changes to track it with chezmoi:

``` numberSource
chezmoi re-add ~/.edited-config # or just chezmoi re-add
```

2.  Check the differences in your editor of choice.
3.  Take action to save or revert.
    - if you like the changes: git commit.
    - if you don’t like the changes: revert changes and `chezmoi apply` to overwrite `$HOME` with the reverted version (before the edits).

> **TIP:**
>
> Always do the `chezmoi re-add` first, as the `chezmoi` directory is being tracked, so it’s okay to be overwritten. You can review the changes in an editor and commit only what’s necessary. However, your `$HOME` is not git tracked, so if you do a `chezmoi apply` first, it overwrites your live files and the previous version is gone.

### Syncing across machines

On the machine where you made changes:

``` numberSource
chezmoi cd
git add -p && git commit -m "..."
git push
```

On the other machine:

``` numberSource
chezmoi cd
git pull
chezmoi diff      # sanity-check
chezmoi apply
```

## References

If you want to explore other features, check out the documentation on the chezmoi homepage:  
<https://www.chezmoi.io/>

------------------------------------------------------------------------

Last modified: 2026-07-05

Back to top
