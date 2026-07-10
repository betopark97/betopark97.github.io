# Workflow

## Choose a Flow

There are a lot of different workflows.  
Git related workflows differ per person and community be it an open-source project or company.

The two that are well recognized like paradigms are **Git Flow** and **GitHub Flow**.

I think the Git Flow is too complex for me so I will go with GitHub Flow. That is not because one is better than the other but you have to consider the size of your project and don’t over complicate stuff.

Git Flow looks something like this:

``` mermaid
gitGraph
    commit id: "init"
    branch develop
    checkout develop
    commit id: "dev start"
    branch feature
    checkout feature
    commit id: "work"
    commit id: "more work"
    checkout develop
    merge feature id: "feature done"
    branch release
    checkout release
    commit id: "rc fixes"
    checkout main
    merge release id: "release" tag: "v1.0"
    checkout develop
    merge release id: "back to dev"
    checkout main
    branch hotfix
    checkout hotfix
    commit id: "urgent fix"
    checkout main
    merge hotfix id: "hotfix" tag: "v1.0.1"
    checkout develop
    merge hotfix id: "sync hotfix"
```

I will not go over the details as I’ve not used this flow so I’m no expert. Might cover it in the future if I get to work on more complex and big projects.

GitHub Flow looks something like this:

``` mermaid
gitGraph
    commit id: "init"
    commit id: "release"
    branch feature
    checkout feature
    commit id: "work"
    commit id: "more work"
    commit id: "review fixes"
    checkout main
    merge feature id: "PR merged" tag: "deploy"
    commit id: "next"
```

The five steps, in words:

1.  **Branch**: make a `feature` branch off `main`.
2.  **Commit**: do the work, one commit at a time.
3.  **Pull Request**: open a PR. Review is a loop, you assign a reviewer for feedback and fix if needed. Repeat until approved.
4.  **Merge**: merge the PR back into `main`.
5.  **Deploy**: `main` ships.

These five steps are all there is. This is quite simple and works for a solo or small dev team.

## Choose a merge strategy

There are three merge strategies that you can choose from: merge, rebase, and squash.

## Workflow Details

let’s add what’s the whole process, something like doing a git status before anything to check if I’ve made a git commit WIP to reset if not just continue

sometimes if I have to switch branches quickly just do a git stash, do something, come back and do git stash pop

then work, git commit

then open a PR: use a good PR template for other people to know what happened

assign someone to review my code

merge the pr

make another feature branch and continue

------------------------------------------------------------------------

Last modified: 2026-07-08

Back to top
