---
name: odoo-dev
description: >
  Develop a new Odoo OCA addon from a GitHub issue or a design document (Word file or
  SharePoint URL) — analyze requirements, scaffold, implement,
  tests (coverage >99%), readme/i18n, and open a PR from ursais to OCA. Use when building a new
  OCA module or implementing a feature issue. One module per branch. Not for migration
  (odoo-migrate), bug fixes (odoo-fix), PR review (odoo-review),
  or estimation (odoo-estimator).
---

# OCA New Module Development

Build a **new** OCA addon from a GitHub issue or a design document, then PR from `ursais` to `OCA/$repo`.

**Platform (shared):** [validation-gate](../shared/validation-gate.md) · [git-commit](../shared/git-commit.md) · [git-one-module](../shared/git-one-module.md) · [ursais-remote](../shared/ursais-remote.md) · [oca-conventions](../shared/oca-conventions.md) · [oca-pr](../shared/oca-pr.md) · [oca-merge-policy](../shared/oca-merge-policy.md) · [testing](../shared/testing.md)

## Invocation

```
/odoo-dev https://github.com/OCA/management-system/issues/42
/odoo-dev ~/Downloads/module-design.docx
/odoo-dev https://…sharepoint.com/…/module-design.docx
```

Ask for a GitHub issue URL or a design document if neither is given. A design document is a Word file (`.docx`) or a SharePoint URL to that file.

## Workflow

```
Step 0  Inputs from issue or design document
Step 1  Claim issue (issue path only) + branch
Step 2  Technical spec
Step 3  Scaffold
Step 4  Implement
Step 5  OCA polish (shared conventions)
Step 6  Tests + i18n + validation gate
Step 7  Push ursais
Step 8  Open PR
Step 9  CI until green
Step 10 Report
```

Working directory: `/tmp/oca-dev/$repo/$repo`

## Core rules

1. One module per branch ([shared/git-one-module.md](../shared/git-one-module.md))  
2. Do not invent scope — ask if the issue is unclear  
3. Validation gate before every commit/push  
4. Push to ursais only ([shared/ursais-remote.md](../shared/ursais-remote.md))  
5. Merge per [shared/oca-merge-policy.md](../shared/oca-merge-policy.md)

## Step 0 — Inputs

One of:

- **GitHub issue** — `$issue_url`. Parse `$repo`, `$ISSUE_NUMBER`, `$target_ver`, and propose `$module`.
- **Design document** — local `.docx` or a SharePoint URL. Read that document as the spec. Ask for `$repo`, `$module`, and `$target_ver` when the document does not state them. Do not invent a GitHub issue.

Details: [references/issue-analysis.md](references/issue-analysis.md)

```bash
[ -z "$GITHUB_TOKEN" ] && echo "ERROR: GITHUB_TOKEN not set" && exit 1
# GitHub issue path only:
gh issue view "$ISSUE_NUMBER" --repo "OCA/$repo" --json title,body,labels,milestone
```

## Step 1 — Branch

```bash
# GitHub issue path only — skip the comment when the input is a design document
gh issue comment "$ISSUE_NUMBER" --repo "OCA/$repo" --body "Working on this in a PR from ursais."
mkdir -p /tmp/oca-dev/$repo && cd /tmp/oca-dev/$repo
git clone https://$GITHUB_TOKEN@github.com/OCA/$repo -b $target_ver --depth=50
cd $repo
# Issue: ${target_ver}-add-${module}-${ISSUE_NUMBER}
# Design document: ${target_ver}-add-${module}
BRANCH="${target_ver}-add-${module}${ISSUE_NUMBER:+-$ISSUE_NUMBER}"
git checkout -b "$BRANCH" origin/$target_ver
[ -d "$module" ] && echo "ERROR: module exists" && exit 1
```

## Steps 2–5 — Spec, scaffold, implement, polish

- Spec checklist: [references/issue-analysis.md](references/issue-analysis.md)  
- Scaffold: [references/module-scaffold.md](references/module-scaffold.md)  
- Polish: [shared/oca-conventions.md](../shared/oca-conventions.md)

## Step 6 — Tests + i18n

Coverage **> 99%** ([shared/validation-gate.md](../shared/validation-gate.md)). Separate `[UPD]` for i18n.

## Steps 7–9 — Push, PR, CI

```bash
git add "$module/"
git commit -m "$(cat <<'EOF'
[ADD] $module

Assisted-by: Cursor <cursoragent@cursor.com>
EOF
)"
# optional [ADD] tests / [UPD] pot after gate — same Assisted-by trailer ([shared/git-commit.md](../shared/git-commit.md))
```

Push: [shared/ursais-remote.md](../shared/ursais-remote.md)  
PR: [shared/oca-pr.md](../shared/oca-pr.md) — title `[${target_ver}][ADD] ${module}: …`, labels `needs review` + `series:` + `mod:`, **milestone `$target_ver`** (never skip), body with **## Test scenario** + deps. GitHub issue: comment `$issue_url`. Design document: link the SharePoint URL or name the Word file in the PR body.

## Step 10 — Report

Issue, module, branch, spec summary, coverage %, PR/labels/CI, merge eligibility, open questions.

## Skill-specific references

| File | Contents |
|------|----------|
| [references/issue-analysis.md](references/issue-analysis.md) | Issue → spec |
| [references/module-scaffold.md](references/module-scaffold.md) | Layout + templates |
