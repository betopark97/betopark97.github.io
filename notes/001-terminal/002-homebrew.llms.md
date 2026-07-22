# Homebrew

## Intro

Homebrew is a package manager for macOS that lets you easily install, update, and manage software tools and applications through the terminal using simple CLI commands.

It is divided into three main components:

- **Formulae (Formulas)**: Package definitions for command-line tools (e.g., brew install python or brew install wget).
- **Casks**: Extensions that let you install full macOS desktop applications, fonts, and plugins (e.g., brew install –cask google-chrome or brew install –cask visual-studio-code).
- **The Cellar**: The local directory on your Mac where Homebrew actually stores all the installed files.

Formulas and casks are what’s installed and the cellar is where it’s stored.

## Installations

Run the command below to install Homebrew.

> **NOTE:**
>
> There will be follow-up prompts, which are very self explanatory.

``` numberSource
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Check that Homebrew was installed successfully:

``` numberSource
brew --version
```

## Useful Commands

This is a compilation of some of the CLI commands that are useful when using Homebrew as your package manager.

### Install Services

Search for the services that you want to install. For example, google something like “brew discord”.

> **NOTE:**
>
> If you are installing a Formulae (CLI Tool & Libraries) it’s different to when you are installing a Cask (GUI Applications)

``` numberSource
# Install a Formulae
brew install {formulae}

# Example
brew install claude-code
```

``` numberSource
# Install a Cask
brew install --cask {cask}

# Example
brew install --cask discord
```

### List Homebrew Services

To list all your brew Formulae and Casks:

``` numberSource
brew list
```

To list only the top level services:

``` numberSource
brew leaves
```

### Update Homebrew and services

To update Homebrew:

``` numberSource
brew update
```

To upgrade a specific services:

``` numberSource
brew upgrade [formula|cask]
```

### Manage Backups

First dump all your services into a file:

``` numberSource
# Dump your files to the path of your choice
brew bundle dump --file="~/path/to/your/Brewfile"

# If you need to overwrite the existing file (to sync new services)
brew bundle dump --force --file="~/path/to/your/Brewfile"
```

To install or restore from your file:

``` numberSource
# To restore everything
brew bundle --file="~/path/to/your/Brewfile"

# To check what's missing without installing
brew bundle check --file="~/path/to/your/Brewfile"

# To install everything in the file and automatically uninstall any extra software in your machine not present in the file
brew bundle --cleanup --file="~/path/to/your/Brewfile"
```

## References

If you want to explore other features, check out the documentation on the Homebrew homepage:  
<https://docs.brew.sh/>

------------------------------------------------------------------------

Last modified: 2026-07-22

Back to top
