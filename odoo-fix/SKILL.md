---
name: odoo-fix
description: >
  Diagnose and fix bugs in Odoo modules from a GitHub issue URL or, when helpdesk_base
  is set in the contributor profile, a helpdesk ticket. Enforces one module per branch,
  tests and coverage (>99%) before every commit/push, one squashed commit, push to your fork never OCA,
  PR with bug/needs review labels. Not for migration (odoo-migrate), new modules (odoo-dev),
  PR review (odoo-review), or estimation (odoo-estimator).
---

# Odoo Module Fix

Reproduce → classify → minimal fix → validate → one squashed commit → fork PR.

**Profile:** [contributor](../shared/contributor.md) — read before push. Stop if `fork_owner` is still `YOUR_GITHUB_ORG`. A helpdesk ticket is accepted only when `helpdesk_base` is set.

**Platform (shared):** [validation-gate](../shared/validation-gate.md) · [git-commit](../shared/git-commit.md) · [git-one-module](../shared/git-one-module.md) · [fork-remote](../shared/fork-remote.md) · [oca-pr](../shared/oca-pr.md) · [oca-merge-policy](../shared/oca-merge-policy.md) · [testing](../shared/testing.md)

## Invocation

```
/odoo-fix https://github.com/OCA/field-service/issues/123
```

Ask for a GitHub issue URL if none is given. When `helpdesk_base` is set, also accept a ticket URL that starts with that prefix.

## Workflow

```
Step 0  Inputs from issue or helpdesk ticket
Step 1  Branch (one module)
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

One of:

- **GitHub issue** — `$issue_url`. Parse owner, `$repo`, `$ISSUE_NUMBER`. Read title, body, labels, milestone with `gh issue view`. Derive `$module`, `$target_ver`, and the symptom from the issue.
- **Helpdesk ticket** — only when `helpdesk_base` is set. The URL must start with that prefix. Read the ticket the user already has open. The symptom comes from the ticket. Ask for `$repo`, `$module`, and `$target_ver` when the ticket does not name them. Do not invent a GitHub issue. If `helpdesk_base` is blank, ask for a GitHub issue instead.

```bash
[ -z "$GITHUB_TOKEN" ] && echo "ERROR: GITHUB_TOKEN not set" && exit 1
# GitHub issue path only:
gh issue view "$ISSUE_NUMBER" --repo "OCA/$repo" --json title,body,labels,milestone
```

## Step 1 — Branch

```bash
# GitHub issue: ${target_ver}-fix-${module}-${ISSUE_NUMBER}
# Helpdesk:     ${target_ver}-fix-${module}-${ticket_id}
BRANCH="${target_ver}-fix-${module}-${ISSUE_NUMBER:-$ticket_id}"
git fetch origin
git checkout -b "$BRANCH" origin/${target_ver}
```

## Steps 2–4 — Reproduce and fix

Evidence: logs, `-i`/`-u`, tests ([shared/testing.md](../shared/testing.md)).  
Patterns: [references/common-failures.md](references/common-failures.md).  
Smallest correct diff; re-run repro until symptom is gone.

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
PR: [shared/oca-pr.md](../shared/oca-pr.md) — title `[FIX] ${module}: …`, labels `bug` + `needs review` + `series:` + `mod:`, **milestone `$target_ver`** (never skip), body **## Test scenario**. GitHub issue: `Fixes …#N` and comment `$issue_url`. Helpdesk ticket: link the ticket URL — do not use `Fixes #N`.  
CI fixes: amend / soft-reset to keep **one** commit; `git push --force-with-lease fork`.

## Step 7 — Report

Issue or helpdesk ticket, symptom, root cause, files, validation (pre-commit/tests/coverage %), test added, branch, 1 commit, PR/labels/milestone, merge eligibility.

## Skill-specific references

| File | Contents |
|------|----------|
| [references/common-failures.md](references/common-failures.md) | Symptom → fix catalog |
