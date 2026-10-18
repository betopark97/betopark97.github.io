# Multiple Accounts

[Setup](../../../notes/002-devops/001-git-github/001-setup.llms.md) gets one GitHub account working on a machine. This page is\
for when a machine needs two or more — typically a work account and a personal\
one — and every repo has to push as the right one.

## The one mental model

Git has two identities, and confusing them causes almost every “it pushed as the\
wrong user” problem.

| Identity | Set by | What it actually does |
|----|----|----|
| **Commit** | `user.name` / `user.email` | Stamps a *label* inside each commit |
| **Auth** | your **SSH key** | Decides which account GitHub thinks you are |

GitHub picks the account **purely from the SSH key**. `user.email` can say\
anything — it will not change which account a push lands under.

Because GitHub refuses to accept the same key on two accounts, each account\
needs its own key, and each repo needs a way to say which key to use.

## Choosing the default

One account keeps plain `github.com` and every other account gets a host alias.

Make the account you use most often the default. Repos already cloned through\
plain `github.com` keep working, so on an established machine the default is\
usually whichever account is already set up — changing it means revisiting every\
existing remote.

The choice is per machine. A work laptop and a personal one will often make\
opposite calls, and nothing in a repo depends on which way a given machine went.

## Adding an account

Three steps, once per extra account per machine. Only the differences from\
[Setup](../../../notes/002-devops/001-git-github/001-setup.llms.md) are spelled out here.

### 1. Generate a key with a distinct filename

``` numberSource
ssh-keygen -t ed25519 -C "you@example.com" -f ~/.ssh/id_ed25519_<alias>
```

`-f` is the part that matters. Without it the new key overwrites the default\
`~/.ssh/id_ed25519`. `-C` is a cosmetic label; the email there has no effect on\
authentication.

### 2. Add the public key to that account

Same as [Setup](../../../notes/002-devops/001-git-github/001-setup.llms.md) — paste `~/.ssh/id_ed25519_<alias>.pub` at\
<https://github.com/settings/ssh/new>.

> **NOTE:**
>
> Log into GitHub **as the account the key belongs to** first, and check the\
> avatar in the top-right before pasting. Adding the key to the wrong account is\
> the most common failure here, and it fails silently until a push goes astray.

### 3. Invent a host alias

This is the glue. `~/.ssh/config` gets a fake hostname that resolves to the real\
GitHub but forces one specific key.

``` numberSource
# ~/.ssh/config

Host github.com-<alias>
  HostName github.com                      # connect to the REAL github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_<alias>   # ...but use THIS key
  IdentitiesOnly yes                       # and only this key
  AddKeysToAgent yes
  UseKeychain yes                          # macOS: remember the passphrase
```

- `Host` — the alias you type in remote URLs. Any string works;\
  `github.com-<alias>` is a readable convention.
- `HostName` — stays real `github.com`.
- `IdentitiesOnly yes` — **required.** Without it SSH offers keys in its own\
  order, hits the default key first, and authenticates as the wrong account.
- The default account needs no block of its own, though giving it one with\
  `IdentitiesOnly yes` keeps the other keys from leaking into its handshake.

Verify each identity independently — the greeting names the account:

``` numberSource
ssh -T git@github.com            # the default account
ssh -T git@github.com-<alias>    # the aliased account
```

Exit code 1 and “does not provide shell access” is normal. Only the name matters.

## Per repo

The **host in the remote URL** is the only thing selecting the account.\
`OWNER/REPO` is identical either way.

| Remote URL                              | Authenticates as    |
|-----------------------------------------|---------------------|
| `git@github.com:OWNER/REPO.git`         | the default account |
| `git@github.com-<alias>:OWNER/REPO.git` | the aliased account |

``` numberSource
# clone
git clone git@github.com-<alias>:OWNER/REPO.git

# or repoint an existing remote
git remote set-url origin git@github.com-<alias>:OWNER/REPO.git
git remote -v    # fetch AND push must both show the alias
```

Auth and authorship are separate, so set the commit identity locally too. Use\
`--global` for the default account only; every aliased account gets a plain\
per-repo `git config`.

``` numberSource
git config user.name  "Your Name"
git config user.email "you@example.com"
```

## Troubleshooting

| Symptom | Cause | Fix |
|----|----|----|
| `Permission to OWNER/REPO.git denied to <other-user>` | Remote uses plain `github.com`, so the default key answered | `git remote set-url origin git@github.com-<alias>:OWNER/REPO.git` |
| Push succeeds but lands under the wrong account | Same cause | `git remote -v`, then repoint as above |
| `ssh -T` greets the wrong name | Public key sits on the wrong account, or `IdentitiesOnly yes` is missing | Re-add the key to the right account; add the flag |
| `ssh -T` asks for a password | `IdentityFile` path is wrong | `ls` the path in the `Host` block |
| Worked before, wrong again after re-adding a remote | `git remote add` with the plain URL silently reverts to the default key | Always type the alias |

**Golden rule:** for any non-default account, the remote host is never plain\
`github.com`.

------------------------------------------------------------------------

Last modified: 2026-09-25

Back to top
