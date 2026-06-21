---
title: Kitty Terminal
---
## Intro

Kitty is a free, open-source, and GPU-accelerated terminal emulator designed for Linux, macOS, and BSD systems.

The key features are:
- GPU Rendering: Offloads text rendering to the graphic card, making it fast and smooth compared to traditional CPU-based terminal emulators.
- Built-in Tiling & Tabs: Features an internal window manager that lets you split screens (horizontally/vertically) and use tabs without needing external tools like `tmux`.
- Scriptable & Extensible: Fully controlled via keyboard shortcuts and supports "Kittens" (small extensions) to do things like view images in the terminal or search for URLs.
- Modern Display Support: Supports TrueColor, ligatures, and specialized protocols for image rendering and keyboard input extensions.

What caught my interest was the GPU rendering, and built-in tiling and tabs. 

---

## Setup

### Binary Install

```shell
curl -L https://sw.kovidgoyal.net/kitty/installer.sh | sh /dev/stdin
```

### Brew Install (Recommended)

```shell
brew install --cask kitty
```

---

## Configurations

The configurations that I've made to Kitty are as follows and it consists of only two files:

- main configurations: `~/.config/kitty/kitty.conf`
- theme configurations: `~/.config/kitty/current-theme.conf`

### kitty.conf

#### Font

| Setting     | Value  | Notes          |
| ----------- | ------ | -------------- |
| `font_size` | `24.0` | Base font size |

#### Window

| Setting                    | Value        | Notes                            |
| -------------------------- | ------------ | -------------------------------- |
| `remember_window_size`     | `yes`        | Reopen at last size              |
| `remember_window_position` | `yes`        | Reopen at last position          |
| `enabled_layouts`          | `tall, grid` | Splitting layouts (multiplexing) |
| `window_border_width`      | `3pt`        | Border thickness                 |
| `draw_minimal_borders`     | `no`         | Draw full borders                |
| `window_padding_width`     | `7`          | Inner padding                    |
| `active_border_color`      | `#fab387`    | Focused window border (peach)    |
| `inactive_border_color`    | `#585b70`    | Unfocused window border          |

#### Appearance

| Setting | Value | Notes |
| --- | --- | --- |
| `background_opacity` | `0.8` | Transparent background |
| `background_blur` | `1` | Blur behind transparency |

#### Keybindings

> [!NOTE] 
> `cmd+enter` is mapped to `no_op` to disable kitty's default new-window shortcut, so `ctrl+shift+enter` is the single binding for new panes.

| Keybinding         | Action                           |
| ------------------ | -------------------------------- |
| `ctrl+shift+enter` | New window (pane) in current dir |
| `cmd+t`            | New tab in current dir           |
| `cmd+n`            | New OS window in current dir     |

All use `launch --cwd=current` so the new tab/window opens in the same directory as the active one. This is done because it's way easier to go back to the root (which is default), but not to a specific project unless your project directory is easy to memorize.

### current-theme.conf

Catppuccin-Mocha (`current-theme.conf`). 

Dark pastel palette: 
- foreground `#CDD6F4`
- background `#1E1E2E`
- accent lilac `#CBA6F7` on active tab

> [!NOTE] 
> This part can be configured with the `kitten themes` command.

---

## Keybindings

The keybindings listed are more than enough in my honest opinion.

### Tabs

This section is for managing the tabs that appear in the bottom.

| Action     | Keybinding           |
| ---------- | -------------------- |
| New Tab    | command + T          |
| Rename Tab | command + I          |
| Switch Tab | command + shift + [] |
| Close Tab  | command + W          |

### Windows (Panes)

This section is for managing the windows (splitting the terminal into multiple panes, i.e. multiplexing).

| Action        | Keybinding           |
| ------------- | -------------------- |
| New window    | ctrl + shift + enter |
| Move window   | ctrl + shift + F     |
| Switch window | ctrl + shift + []    |
| Close window  | ctrl + shift + W     |