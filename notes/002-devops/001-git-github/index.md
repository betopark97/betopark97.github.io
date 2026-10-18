---
title: "Git & GitHub"
icon: "simple-icons:github"
description: "Version control with Git, and the pull-request flow GitHub builds on it."
---
Git is a local software tool that tracks changes to your code files over time (version control).

GitHub is an online, cloud-based platform used to host those tracked files so you can back them up and collaborate with other developers.

Git is the engine, GitHub is the network.

There are various version control tools and various collaboration cloud platforms, but I will choose the mainstream and battle-tested one.

## Reading Path

| Page | What it answers |
| --- | --- |
| [Setup](001-setup.md) | How do I install git and authenticate to GitHub from a new machine? |
| [Workflow](002-workflow.qmd) | What do I actually do, from `git status` to a merged pull request? |
| [Merge Strategies](003-merge-strategies.qmd) | Which merge button, and why does my branch diverge afterwards? |
| [CI/CD](004-ci-cd.md) | What runs automatically once a change lands? |
| [Conventions](005-conventions.md) | How do I name a branch, write a commit, shape a pull request? |
| [Multiple Accounts](006-multiple-accounts.md) | How do I run a second GitHub account on the same machine? |

Mid-task and just need the loop: `git checkout main && git pull`, branch, commit,
push, PR, merge in the browser, delete the branch.
