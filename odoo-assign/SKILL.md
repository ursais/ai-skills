---
name: odoo-assign
description: >
  Assign an OCA GitHub issue or pull request to a module maintainer. Use when
  odoo-fix cannot fix an issue, when a pull request is ready for human testing,
  or when the user runs /odoo-assign. If the module has no maintainer, assign
  the Project Steering Committee member with the fewest open assigned issues
  and pull requests. When the issue or pull request has no milestone and no
  labels, set them the same way odoo-review does. This is the only skill that
  sets GitHub assignees. Not for writing the fix (odoo-fix), reviewing
  (odoo-review), merging (odoo-merge), or rebasing (odoo-rebase).
---

# Odoo assign

Set the GitHub assignee on one OCA issue or pull request. No other skill sets assignees.

## Invocation

```
/odoo-assign https://github.com/OCA/field-service/issues/123
/odoo-assign https://github.com/OCA/field-service/pull/456
/odoo-assign OCA/field-service#456
```

Ask for the URL if it is missing. Requires `gh` authenticated with permission to read the OCA repository and add assignees.

Called from [odoo-fix](../odoo-fix/SKILL.md) when that skill stops without a fix, and from [odoo-review](../odoo-review/SKILL.md) when Gate C is ready for human testing. The same rules apply when the user runs this skill directly.

## Workflow

```
Step 1  Parse the issue or pull request
Step 2  Resolve the module and the series branch
Step 3  If there is no milestone and no labels, set both
Step 4  Read maintainers from __manifest__.py
Step 5  If none, load the repository PSC
Step 6  Pick the login with the fewest open assignments in this repo
Step 7  Add that login; do not remove anyone already assigned
```

### Step 1 — Parse

Accept an issue URL, a pull request URL, or `owner/repo#number`. The issue or pull request must live on `OCA/$repo`.

```bash
gh issue view "$NUMBER" --repo "OCA/$repo" --json number,title,labels,milestone,assignees
# pull request: also
gh pr view "$NUMBER" --repo "OCA/$repo" \
  --json number,baseRefName,headRefName,headRepositoryOwner,files,labels,assignees
```

### Step 2 — Module and series

| Input | `$target_ver` | `$module` |
|-------|----------------|-----------|
| Pull request | `baseRefName` | `mod:` label, otherwise the single addon directory in the diff |
| Issue | milestone title, otherwise the `series:` label, otherwise a single `N.0` in the title | `mod:` label, otherwise a single technical module name in the title |

One addon only. If the diff touches several addons, or the issue does not name exactly one module, stop and ask which module. Do not guess an assignee. If an issue still has no series, stop and ask. Do not guess the series.

### Step 3 — Milestone and labels when both are missing

Run this step only when `milestone` is null **and** `labels` is empty. If either is already set, leave milestone and labels unchanged and continue at Step 4.

Use `gh api` REST, not `gh issue edit` or `gh pr edit`. Same packaging as [odoo-review](../odoo-review/SKILL.md) Gate B and [oca-pr](../shared/oca-pr.md):

| Field | Value |
|-------|--------|
| Milestone | `$target_ver` (create it open if missing) |
| Labels | add `needs review`, `series:$target_ver`, `mod:$module` |

Create a missing label before adding it. Copy the color of an existing `series:` label, or use `1D76DB`. `mod:` is `5319E7`. `needs review` is `fbca04` when the repo has no `needs review` label yet. Do not remove labels.

```bash
MILESTONE_NUM=$(gh api "repos/OCA/$repo/milestones" --paginate \
  --jq ".[] | select(.title==\"$target_ver\") | .number")
if [ -z "$MILESTONE_NUM" ]; then
  MILESTONE_NUM=$(gh api -X POST "repos/OCA/$repo/milestones" \
    -f title="$target_ver" -f state=open --jq .number)
fi
gh api -X PATCH "repos/OCA/$repo/issues/$NUMBER" -F milestone="$MILESTONE_NUM"

SERIES_COLOR=$(gh api "repos/OCA/$repo/labels" --paginate \
  --jq '[.[] | select(.name|startswith("series:"))][0].color // "1D76DB"')
gh api -X POST "repos/OCA/$repo/labels" -f name="needs review" -f color="fbca04" || true
gh api -X POST "repos/OCA/$repo/labels" -f name="series:${target_ver}" -f color="$SERIES_COLOR" || true
gh api -X POST "repos/OCA/$repo/labels" -f name="mod:${module}" -f color="5319E7" || true
gh api -X POST "repos/OCA/$repo/issues/$NUMBER/labels" \
  -f 'labels[]=needs review' \
  -f "labels[]=series:${target_ver}" \
  -f "labels[]=mod:${module}"

gh issue view "$NUMBER" --repo "OCA/$repo" --json milestone,labels \
  --jq '{milestone: .milestone.title, labels: [.labels[].name]}'
```

Fail this step if the milestone title is not `$target_ver`, or if `needs review`, `series:$target_ver`, or `mod:$module` is missing. Do not set an assignee in this step.

### Step 4 — Module maintainers

Read `$module/__manifest__.py` on `OCA/$repo` at `$target_ver`:

```bash
gh api "repos/OCA/$repo/contents/${module}/__manifest__.py?ref=${target_ver}" --jq .content
```

Decode the content and take the `maintainers` list (GitHub logins). If the file is missing on that branch and the input is a pull request, read the same path from the PR head repository and head ref.

A missing key or an empty list means there is no module maintainer. Continue at Step 5.

### Step 5 — PSC when there is no maintainer

PSC members are the GitHub team `OCA/${repo}-maintainers` (for example `field-service-maintainers`).

```bash
gh api --paginate "orgs/OCA/teams/${repo}-maintainers/members" --jq '.[].login'
```

If that team does not exist, list `repos/OCA/$repo/teams` and use the slug that ends with `-maintainers` and is not `core-maintainers` and does not contain `psc-representative`. Do not use `board` or `core-maintainers`.

Skip logins that contain `bot` (for example `OCA-git-bot`, `oca-transbot`). If nobody remains, stop and report that. Do not assign the authenticated user.

### Step 6 — Least loaded

Candidates are the module maintainers when that list is non-empty, otherwise the PSC members from Step 5.

For each candidate, count open issues and pull requests already assigned to them in this repository. GitHub's issue search includes both:

```bash
gh api --method GET search/issues \
  -f q="repo:OCA/${repo} assignee:${login} is:open" \
  -f per_page=1 --jq .total_count
```

Choose the lowest count. Tie-break is the order in the manifest, or alphabetical login for PSC members.

### Step 7 — Assign

Add the chosen login. Do not remove people already assigned. If that login is already an assignee, leave the issue or pull request unchanged.

```bash
gh api -X POST "repos/OCA/$repo/issues/$NUMBER/assignees" \
  -f "assignees[]=${CHOSEN}"
```

## Report

URL, issue or pull request, module, series, whether milestone and labels were set in this run, whether the person came from the manifest or the PSC, the chosen login, their open assignment count, the other candidates' counts, and whether the assignee was added or was already set.
