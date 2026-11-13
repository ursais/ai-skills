---
name: odoo-rebase
description: >
  Rebase an Odoo/OCA pull request head onto its base branch when the source (head)
  repository is under the ursais org. Use when rebasing a PR, /odoo-rebase, or when a
  PR needs updating onto the target series. Not for merging (odoo-merge), reviewing
  (odoo-review), writing modules (odoo-dev), migrations (odoo-migrate), or fixes
  (odoo-fix).
---

# Odoo Rebase

Take `$pr_url`, verify the **head (source) repo is under `ursais`**, then **rebase** that head branch onto the PR base and push with `--force-with-lease`.

**Platform (shared):** [ursais-remote](../shared/ursais-remote.md) · [git-commit](../shared/git-commit.md)

## Invocation

```
/odoo-rebase https://github.com/OCA/field-service/pull/1234
/odoo-rebase OCA/field-service#1234
```

Ask for `$pr_url` if missing. Requires `gh` + `git` and push access to `ursais/$repo`.

## Workflow

```
Step 0  Parse PR + head/base metadata
Step 1  Gate: head owner must be ursais
Step 2  Local checkout of head branch
Step 3  Rebase onto base + push --force-with-lease
Step 4  Report
```

Do **not** rebase or force-push when the head is not under `ursais`. Do **not** push to `OCA` / `origin` as a write remote for the base repo.

## Core rules

1. **Head repository owner must be `ursais`** (exact login). Otherwise stop and report — no clone, no rebase, no push.  
2. Rebase onto the PR **base** ref (`baseRefName`) only.  
3. Push only to **`ursais`** with `--force-with-lease` ([ursais-remote](../shared/ursais-remote.md)).  
4. On conflict: resolve only if straightforward; otherwise `git rebase --abort`, push nothing, list conflicting files.  
5. Do not amend messages or squash unless the user asks — rebase only.  
6. Never `git push` to the base/OCA remote.

## Step 0 — Inputs

```bash
[ -z "$(gh auth token 2>/dev/null)" ] && echo "ERROR: gh not authenticated" && exit 1
TOKEN=$(gh auth token)

# Parse BASE_OWNER, repo, PR_NUMBER from URL or Owner/repo#N
gh pr view "$PR_NUMBER" --repo "$BASE_OWNER/$repo" \
  --json url,title,baseRefName,headRefName,headRepository,headRepositoryOwner,isCrossRepository,isDraft,mergeable
```

| Variable | Source |
|----------|--------|
| `$BASE_OWNER/$repo` | PR base repository |
| `$BASE_BRANCH` | `baseRefName` (e.g. `19.0`) |
| `$HEAD_OWNER` | `headRepositoryOwner.login` |
| `$HEAD_REPO` | `headRepository.name` |
| `$HEAD_BRANCH` | `headRefName` |

## Step 1 — ursais gate

```bash
if [ "$HEAD_OWNER" != "ursais" ]; then
  echo "BLOCKED: source (head) owner is '$HEAD_OWNER' — required: ursais. Will not rebase."
  exit 1
fi
```

Allowed example: base `OCA/$repo`, head `ursais:$HEAD_BRANCH`.  
Blocked: personal forks, other orgs, or same-repo heads on `OCA` without a ursais head.

## Step 2 — Checkout

```bash
WORKDIR=/tmp/oca-rebase/${BASE_OWNER}-${repo}-${PR_NUMBER}
rm -rf "$WORKDIR"
mkdir -p /tmp/oca-rebase

git clone "https://x-access-token:${TOKEN}@github.com/ursais/${HEAD_REPO}.git" "$WORKDIR"
cd "$WORKDIR"

git remote add upstream "https://github.com/${BASE_OWNER}/${repo}.git" 2>/dev/null || \
  git remote set-url upstream "https://github.com/${BASE_OWNER}/${repo}.git"

git fetch upstream "$BASE_BRANCH"
git fetch origin "$HEAD_BRANCH"
git checkout -B "$HEAD_BRANCH" "origin/$HEAD_BRANCH"
```

`origin` = `ursais/$HEAD_REPO` (write). `upstream` = base repo (fetch only).

## Step 3 — Rebase and push

```bash
git rebase "upstream/$BASE_BRANCH"
# On conflict: fix + `git rebase --continue`, or `git rebase --abort` and stop (no push)

git push --force-with-lease origin "$HEAD_BRANCH"
```

Confirm the PR head moved:

```bash
gh pr view "$PR_NUMBER" --repo "$BASE_OWNER/$repo" --json url,mergeable,headRefOid
```

## Step 4 — Report

- PR link  
- **rebased** / **blocked** (non-ursais head) / **conflicts** (paths)  
- `ursais/$HEAD_REPO:$HEAD_BRANCH` onto `$BASE_OWNER/$repo:$BASE_BRANCH`  
- New head SHA if pushed  

After a successful rebase, CI re-runs on the PR; use `odoo-review` / `odoo-merge` separately if needed.
