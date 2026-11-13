---
name: odoo-migrate
description: >
  Migrate an OCA module between Odoo versions and open a PR from your fork to OCA. Use when migrating
  or porting an OCA module (e.g. to 17.0/18.0/19.0/20.0), creating a migration branch in your fork, or
  opening an OCA migration PR. One module per branch and PR. Runs pre-commit, tests, and coverage
  (>99%) before every commit/push. Not for new modules (odoo-dev), bug fixes (odoo-fix),
  or PR review (odoo-review).
---

# OCA Module Migration

Migrate `$module` in `OCA/$repo` from `$source_ver` → `$target_ver`, push from `$fork_owner`, open PR, CI green.

**Profile:** [contributor](../shared/contributor.md) — read before clone, push, or copyright. Stop if `fork_owner` or the author fields are still `YOUR_*`.

**Platform (shared):** [validation-gate](../shared/validation-gate.md) · [git-commit](../shared/git-commit.md) · [git-one-module](../shared/git-one-module.md) · [fork-remote](../shared/fork-remote.md) · [oca-conventions](../shared/oca-conventions.md) · [oca-pr](../shared/oca-pr.md) · [oca-merge-policy](../shared/oca-merge-policy.md) · [testing](../shared/testing.md)

## Workflow

```
Step 0  Inputs
Step 1  Clone + verify module on $source_ver
Step 2  Branch + git am (-- $module) + same-author squash
Step 3  Migrate + conventions + tests (>99% coverage) → [MIG] / [UPD]
Step 4  Push once to fork
Step 5  Open PR (migration labels, deps in body, /ocabot)
Step 6  CI until green
Step 7  Report
```

Working directory: `/tmp/oca-mig/$repo/$repo`

## Core rules

1. Local-first — 0 pushes until Step 3 done; then 1 open + ≤1 CI fix push  
2. Validation gate before every commit/push ([shared/validation-gate.md](../shared/validation-gate.md))  
3. Preserve migration commit chain — same-author squash only ([references/git-squash.md](references/git-squash.md))  
4. One module per branch ([shared/git-one-module.md](../shared/git-one-module.md))  
5. `[UPD] Update ${module}.pot` separate from `[MIG]`

## Prerequisites

`GITHUB_TOKEN`, `git`, `pre-commit`, `gettext`, `coverage`, Odoo test harness.

```bash
[ -z "$GITHUB_TOKEN" ] && echo "ERROR: GITHUB_TOKEN not set" && exit 1
```

## Step 0 — Inputs

| Variable | Example | Notes |
|----------|---------|-------|
| `$repo` | `management-system` | OCA repo |
| `$module` | `mgmtsystem_action` | One module only |
| `$source_ver` | `18.0` | Default: `$target_ver - 1` |
| `$target_ver` | `20.0` | Target branch (17.0 / 18.0 / 19.0 / 20.0 supported) |
| `$PR_ASSIGNEE` | profile `maintainer` | Blank maintainer: `gh api user -q .login` |

Multiple modules → separate full runs.

## Step 1 — Verify and clone

```bash
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/OCA/$repo/contents/$module?ref=$source_ver" \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('name','NOT FOUND'))"

mkdir -p /tmp/oca-mig/$repo && cd /tmp/oca-mig/$repo
git clone https://$GITHUB_TOKEN@github.com/OCA/$repo -b $target_ver --depth=50
cd $repo && git fetch origin $source_ver
```

## Step 2 — Branch + history

```bash
BRANCH="${target_ver}-mig-${module}"
git checkout -b "$BRANCH" origin/$target_ver
git format-patch --keep-subject --stdout origin/$target_ver..origin/$source_ver -- $module \
  | git am -3 --keep
```

`-- $module` is mandatory. On failure: abort, retry `--ignore-whitespace`, or resolve manually.
Verify one module ([shared/git-one-module.md](../shared/git-one-module.md)).
Same-author squash only: [references/git-squash.md](references/git-squash.md).

## Step 3 — Migrate

1. Version guide: `references/migration-${target_ver}.md` (17.0–20.0) or OCA wiki `Migration-to-version-${target_ver}` — when jumping versions, apply **all** intermediate guides  
2. Tasks: [references/step-3-tasks.md](references/step-3-tasks.md) + [shared/oca-conventions.md](../shared/oca-conventions.md)  
3. **Enough unit tests** for coverage **> 99%** before `[MIG]`  
4. Validation gate → commit:

```bash
git add "$module/" && git reset HEAD -- "$module/i18n/"
git commit -m "$(cat <<'EOF'
[MIG] $module: Migration to $target_ver

Assisted-by: Cursor <cursoragent@cursor.com>
EOF
)"
# optional: [ADD] unit tests before or with MIG
git add "$module/i18n/" && git commit -m "$(cat <<'EOF'
[UPD] Update ${module}.pot

Assisted-by: Cursor <cursoragent@cursor.com>
EOF
)"  # after gate
```

## Step 4 — Push

[shared/fork-remote.md](../shared/fork-remote.md) — push `$BRANCH` once.

## Step 5 — PR

[shared/oca-pr.md](../shared/oca-pr.md)

- Title: `[${target_ver}][MIG] ${module}: Migration to ${target_ver}`  
- Labels + **milestone `$target_ver`**: `needs review`, `migration`, `series:`, `mod:` (+ `blocked by dependency` if needed) — never skip milestone  

- Body: **## Test scenario** (required) + **## Dependencies** (no separate deps comment)  
- Comment: `/ocabot migration ${module}` only  

## Step 6 — CI

[shared/oca-pr.md](../shared/oca-pr.md) CI loop. Merge per [shared/oca-merge-policy.md](../shared/oca-merge-policy.md).

## Step 7 — Report

Module, branch, squash before→after, changes, coverage %, tests added, push count, PR/labels/ocabot/CI, merge eligibility, TODOs.

## Skill-specific references

| File | Contents |
|------|----------|
| [references/step-3-tasks.md](references/step-3-tasks.md) | Migration checklist + tests/i18n |
| [references/git-squash.md](references/git-squash.md) | Same-author squash |
| [references/migration-17.0.md](references/migration-17.0.md) | 17.0 framework |
| [references/migration-18.0.md](references/migration-18.0.md) | 18.0 framework |
| [references/migration-19.0.md](references/migration-19.0.md) | 19.0 framework |
| [references/migration-20.0.md](references/migration-20.0.md) | 20.0 framework ([OCA wiki](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-20.0)) |
| [scripts/squash-same-author.py](scripts/squash-same-author.py) | Rebase sequence editor |
