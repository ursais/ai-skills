---
name: odoo-fix
description: >
  Fix one OCA module from a GitHub issue. Tests and coverage >99%, one commit, PR from
  your fork. Does not assign. If it cannot fix, hand off to odoo-assign. Use for
  /odoo-fix. Not for migrate, new modules, review, or assign.
---

# Odoo Module Fix

Reproduce → classify → minimal fix → validate → one squashed commit → fork PR.

**Profile:** [contributor](../shared/contributor.md) — read before push. Stop if `fork_owner` is still `YOUR_GITHUB_ORG`.

**Platform (shared):** [validation-gate](../shared/validation-gate.md) · [git-commit](../shared/git-commit.md) · [git-one-module](../shared/git-one-module.md) · [fork-remote](../shared/fork-remote.md) · [oca-pr](../shared/oca-pr.md) · [oca-merge-policy](../shared/oca-merge-policy.md) · [testing](../shared/testing.md). Read a linked file only in the step that needs it.

## Invocation

```
/odoo-fix https://github.com/OCA/field-service/issues/123
```

Ask for a GitHub issue URL if none is given.

## Workflow

```
Step 0  Inputs from the GitHub issue
Step 1  Branch + package the GitHub issue
Step 2  Reproduce
Step 3  Classify → fix pattern
Step 4  Minimal fix (no commits yet)
Step 5  Validation gate
Step 6  One squashed commit → push → PR
Step 7  Report
```

## Core rules

1. Reproduce before editing  
2. One module per branch ([shared/git-one-module.md](../shared/git-one-module.md))  
3. Minimal diff  
4. Validation gate before commit/push ([shared/validation-gate.md](../shared/validation-gate.md))  
5. **Squash all changes in one commit** (OCA will not merge multi-commit fix PRs)  
6. Push to `$fork_owner` only ([shared/fork-remote.md](../shared/fork-remote.md))  
7. Add/extend tests for logic bugs — keep coverage > 99%  
8. Merge per [shared/oca-merge-policy.md](../shared/oca-merge-policy.md)

## Step 0 — Inputs

**GitHub issue** — `$issue_url`. Parse owner, `$repo`, `$ISSUE_NUMBER`. Read title, body, labels, milestone with `gh issue view`. Derive `$module`, `$target_ver`, and the symptom from the issue. Require a GitHub issue URL.

```bash
[ -z "$GITHUB_TOKEN" ] && echo "ERROR: GITHUB_TOKEN not set" && exit 1
gh issue view "$ISSUE_NUMBER" --repo "OCA/$repo" --json title,body,labels,milestone
```

## Step 1 — Branch and issue packaging

```bash
# ${target_ver}-fix-${module}-${ISSUE_NUMBER}
BRANCH="${target_ver}-fix-${module}-${ISSUE_NUMBER}"
git fetch origin
git checkout -b "$BRANCH" origin/${target_ver}
```

Set these fields on `OCA/$repo#$ISSUE_NUMBER` before editing code. Use `gh api` REST, not `gh issue edit`.

| Field | Value |
|-------|--------|
| Milestone | `$target_ver` (create it open if missing; never skip) |
| Type | `Bug` |
| Labels | add `bug`, `series:$target_ver`, `mod:$module` — do not remove labels already on the issue |

Do not set assignees. Only [odoo-assign](../odoo-assign/SKILL.md) does that.

```bash
MILESTONE_NUM=$(gh api "repos/OCA/$repo/milestones" --paginate \
  --jq ".[] | select(.title==\"$target_ver\") | .number")
if [ -z "$MILESTONE_NUM" ]; then
  MILESTONE_NUM=$(gh api -X POST "repos/OCA/$repo/milestones" \
    -f title="$target_ver" -f state=open --jq .number)
fi
gh api -X PATCH "repos/OCA/$repo/issues/$ISSUE_NUMBER" \
  -f type=Bug -F milestone="$MILESTONE_NUM"

SERIES_COLOR=$(gh api "repos/OCA/$repo/labels" --paginate \
  --jq '[.[] | select(.name|startswith("series:"))][0].color // "1D76DB"')
gh api -X POST "repos/OCA/$repo/labels" -f name="bug" -f color="D73A4A" -f description="Something is not working" || true
gh api -X POST "repos/OCA/$repo/labels" -f name="series:${target_ver}" -f color="$SERIES_COLOR" || true
gh api -X POST "repos/OCA/$repo/labels" -f name="mod:${module}" -f color="5319E7" || true
gh api -X POST "repos/OCA/$repo/issues/$ISSUE_NUMBER/labels" \
  -f 'labels[]=bug' \
  -f "labels[]=series:${target_ver}" \
  -f "labels[]=mod:${module}"

gh issue view "$ISSUE_NUMBER" --repo "OCA/$repo" \
  --json type,milestone,labels \
  --jq '{type: .type.name, milestone: .milestone.title, labels: [.labels[].name]}'
```

Fail the step if `type` is not `Bug`, the milestone title is not `$target_ver`, or `bug`, `series:$target_ver`, or `mod:$module` is missing.

## Steps 2–4 — Reproduce and fix

Evidence: logs, `-i`/`-u`, tests ([shared/testing.md](../shared/testing.md)).  
Patterns: [references/common-failures.md](references/common-failures.md).  
Smallest correct diff; re-run repro until symptom is gone.

## When you cannot fix

Stop without a commit or a pull request when you cannot reproduce the bug, the safe fix is not clear, the change is out of scope for this module, or the user says not to change code. Then follow [odoo-assign](../odoo-assign/SKILL.md) for this issue in the same run. Do not call the assignees API from this skill.

## Step 5 — Validation gate

[shared/validation-gate.md](../shared/validation-gate.md) — no commits until green.

## Step 6 — Commit, push, PR

```bash
# soft-reset if multiple WIP commits
git reset --soft origin/${target_ver}
git add "$module/"
git commit -m "$(cat <<'EOF'
[FIX] $module: <concise root cause>

Assisted-by: Cursor <cursoragent@cursor.com>
EOF
)"
```

Push: [shared/fork-remote.md](../shared/fork-remote.md)  
PR: [shared/oca-pr.md](../shared/oca-pr.md) — title `[FIX] ${module}: …`, labels `bug` + `needs review` + `series:` + `mod:`, **milestone `$target_ver`** (never skip), body **## Test scenario**. Link the issue with `Fixes …#N` and comment `$issue_url`.  
CI fixes: amend / soft-reset to keep **one** commit; `git push --force-with-lease fork`.

The PR **description** must ask the issue author to review and test. Read the author with `gh issue view "$ISSUE_NUMBER" --repo "OCA/$repo" --jq .author.login`. Put this after the test scenario, using their login:

```markdown
@$issue_author please review and test this fix.
```

Also request that login as a PR reviewer (`requested_reviewers`), unless it is the authenticated user who opened the PR.

## Step 7 — Report

Issue, symptom, root cause, files, validation (pre-commit/tests/coverage %), test added, branch, 1 commit, issue type/milestone/labels, PR/labels/milestone, whether the issue author was asked to review and test, merge eligibility. If you stopped without a fix, say that and the assignee `odoo-assign` chose.

## Skill-specific references

| File | Contents |
|------|----------|
| [references/common-failures.md](references/common-failures.md) | Symptom → fix catalog |
