---
title: Setup
---
## Git

### Installation

If you're on mac, it's already installed so just check the version.

```shell
git --version
```

If you are on linux (Ubuntu) do a sudo install.

```shell
sudo apt update
sudo apt install git -y
```

### Configurations

Git requires an identification.

```shell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## GitHub

Go to https://github.com/ and create an account.

### SSH key Authentication

This is a key-pair authentication. SSH authentication uses a pair of keys that work like a lock and key:

- Private Key (id_ed25519): Stays strictly on your computer. Never share this.
- Public Key (id_ed25519.pub): Acts as the lock that only your private key can open. Upload this to GitHub.

#### Step 1: Generate a new SSH key pair

```shell
ssh-keygen -t ed25519 -C "your.email@example.com"
```

Some prompts will appear asking:

- where to save they keys, press Enter to accept the default location (`~./ssh`).
- for a passphrase, press Enter to leave it empty (convenient), or type a password for extra security.

> [!NOTE]
> If you decide to enter a passphrase, be aware that the terminal will not show any visual feedback (such as asterisks or characters) while you are typing. Simply type the passphrase fully and press Enter.

#### Step 2: Add the SSH Key to the ssh-agent

The ssh-agent is what manages your keys in the background.

1. Start the agent:

```shell
eval "$(ssh-agent -s)"
```

2. Add your private key to the agent:

```shell
ssh-add ~/.ssh/id_ed25519
```

#### Step 3: Add the Public Key to GitHub

1. Copy the public key's content to your clipboard:

```shell
pbcopy < ~/.ssh/id_ed25519.pub
```

2. Go to GitHub, click your profile picture (top-right corner), and then **Settings**.
3. In the left sidebar, click **SSH and GPG keys**.
4. Click **New SSH key** (green button top-right).
5. Give it a descriptive title of your local machine (e.g., "my-mac") and paste your key from the clip board.
6. Click **Add SSH key**.

#### Step 4: Test the Connection

```shell
ssh -T git git@github.com
```

If you see a message like the following, then you are good to go.

```text
Hi {username}! You've successfully authenticated, but GitHub does not provide shell access.
```

***

[Last modified: 2026-07-06]{.note-modified}
