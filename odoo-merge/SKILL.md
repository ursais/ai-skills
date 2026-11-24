---
name: odoo-merge
description: >
  Merge an OCA pull request when CI, human approvals, age, and coverage already
  pass. OCA uses /ocabot merge. Never approves. Use for /odoo-merge. Not for
  review, rebase, or writing the change.
---

# Odoo Merge

Evaluate `$pr_url` against merge gates. If all pass, **merge** (OCA: ocabot comment; else GitHub API). If any fail, **do not merge** — report blockers only.

Do **not** approve the pull request. Approvals counted by the gates must already come from a human who tested. Never submit `APPROVE` or `gh pr review --approve`.

**Platform (shared):** [oca-merge-policy](../shared/oca-merge-policy.md) · [oca-pr](../shared/oca-pr.md) · [git-commit](../shared/git-commit.md). Read a linked file only in the step that needs it.

## Invocation

```
/odoo-merge https://github.com/OCA/field-service/pull/1234
/odoo-merge OCA/field-service#1234
/odoo-merge https://github.com/example/some-repo/pull/99
```

Ask for `$pr_url` if missing. Requires `gh` authenticated with permission to comment (OCA) or merge (non-OCA).

## Workflow

```
Step 0  Parse PR + owner/repo
Step 1  Collect gates (CI, reviews, age, coverage, mergeability)
Step 2  Decide: ready or blocked
Step 3  If ready → OCA ocabot comment OR GitHub merge
Step 4  Report to user
```

Do **not** force-merge, bypass branch protection, or post `/ocabot merge` when any gate fails.

## Core rules

1. Gates from [oca-merge-policy](../shared/oca-merge-policy.md) **plus** coverage (below) — all must pass  
2. **`$OWNER == OCA`** (case-sensitive org) → comment `/ocabot merge <bump>`; never `gh pr merge` on OCA  
3. **Any other owner** → merge with GitHub API (`gh pr merge`)  
4. Choose **patch** / **minor** / **major** from the diff ([references/semver-bump.md](references/semver-bump.md))  
5. Draft PRs, conflicts, or red/pending required checks → blocked

## Step 0 — Inputs

```bash
[ -z "$(gh auth token 2>/dev/null)" ] && echo "ERROR: gh not authenticated" && exit 1

# Parse OWNER, repo, PR_NUMBER from URL or Owner/repo#N
gh pr view "$PR_NUMBER" --repo "$OWNER/$repo" \
  --json title,url,author,baseRefName,isDraft,mergeable,mergeStateStatus,reviewDecision,createdAt,labels,files,commits,statusCheckRollup
```

Set `$IS_OCA=true` when `$OWNER` is `OCA`.

## Step 1 — Gates

### 1a — Draft / conflicts

| Check | Pass when |
|-------|-----------|
| Draft | `isDraft == false` |
| Mergeable | `mergeable == MERGEABLE` (not `CONFLICTING`) |

### 1b — CI

```bash
gh pr checks "$PR_NUMBER" --repo "$OWNER/$repo"
```

- Every **required** / non-skipped check must be **pass**  
- Any **fail** → blocked  
- Any **pending** / **queued** → blocked (wait; do not merge)  
- Ignored alone: optional skipped checks

### 1c — Code coverage

From checks / status rollup, treat coverage as a gate:

| Check | Required |
|-------|----------|
| `codecov/patch`, `codecov/patch/*`, or similarly named **patch** coverage | Must be **pass** (or absent if the repo has no coverage check) |
| `codecov/project` / project-only | **Not** a blocker if patch is green (or no patch check exists) |

If a patch coverage check exists and is fail/pending → blocked.

### 1d — Reviews and duration

Apply [oca-merge-policy](../shared/oca-merge-policy.md):

```bash
gh pr view "$PR_NUMBER" --repo "$OWNER/$repo" \
  --json createdAt,reviews,author,reviewDecision \
  --jq '{
    created: .createdAt,
    age_days: ((now - (.createdAt | fromdateiso8601)) / 86400 | floor),
    approvals: (.author.login as $a | [.reviews[] | select(.state == "APPROVED" and .author.login != $a)] | unique_by(.author.login) | length),
    changes_requested: ([.reviews[] | select(.state == "CHANGES_REQUESTED")] | length),
    review_decision: .reviewDecision
  }'
```

| Gate | Pass when |
|------|-----------|
| Age | `age_days >= 5` |
| Reviews | `approvals >= 2` (or `>= 3` if repo/PSG requires it), **or** `approvals == 0` (no-review fallback after 5 days) |
| Changes requested | No outstanding `CHANGES_REQUESTED` from a reviewer that was not superseded by a later approval from that reviewer; if `reviewDecision == CHANGES_REQUESTED` → blocked |
| Labels | No `needs fixing` (or equivalent) unless the user explicitly overrides |

**One approval only** after 5 days → blocked (need a second review).

### Gate summary

All of 1a–1d must pass before Step 3. On any failure, skip merge and list blockers in Step 4.

## Step 2 — Semver bump (OCA only)

If `$IS_OCA` and gates pass, pick **one** bump from what operators must do after deploy (see [references/semver-bump.md](references/semver-bump.md)):

| Bump | Meaning |
|------|---------|
| `patch` | A server restart is enough for the changes to take effect |
| `minor` | The module needs to be upgraded |
| `major` | The changes need a migration script that is provided in the pull request |

If `major` is warranted but the PR has **no** migration script → **block** (do not comment `/ocabot merge`). Otherwise choose and state the rationale (restart / `-u` / script path) in the report.

## Step 3 — Merge action

### OCA (`$OWNER == OCA`)

```bash
gh pr comment "$PR_NUMBER" --repo "OCA/$repo" --body "/ocabot merge $BUMP"
# $BUMP is patch | minor | major
```

Do **not** also run `gh pr merge` on OCA — ocabot owns the merge.

### Non-OCA

```bash
# Prefer squash unless repo forbids it; fall back to merge commit
gh pr merge "$PR_NUMBER" --repo "$OWNER/$repo" --squash --delete-branch \
  || gh pr merge "$PR_NUMBER" --repo "$OWNER/$repo" --merge --delete-branch
```

If branch protection or permissions block the merge, stop and report the API error — do not work around with admin overrides unless the user explicitly asks.

## Step 4 — Report

Short message:

- PR link + **merged** / **blocked**
- Gate table: CI, coverage, age_days, approvals, draft/conflicts
- If merged: method (`/ocabot merge $BUMP` or `gh pr merge --squash`) + comment/merge URL
- If blocked: checkbox list of what is still missing

## Skill-specific references

| File | Contents |
|------|----------|
| [references/semver-bump.md](references/semver-bump.md) | patch / minor / major decision guide |
