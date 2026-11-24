---
name: odoo-report
description: >
  Create an OCA GitHub bug issue from a stacktrace, log, or user notes. Sets the
  series milestone and the bug label. Use for /odoo-report. Not for fixing
  (odoo-fix), assigning (odoo-assign), or reviewing (odoo-review).
---

# Odoo report

Turn a stacktrace, a log, or notes into one GitHub issue on `OCA/$repo`. Do not change code, open a pull request, or set an assignee.

## Invocation

```
/odoo-report
/odoo-report OCA/field-service
```

Ask for the OCA repository if it is missing. Requires `gh` authenticated with permission to open issues on that repository.

## Workflow

```
Step 1  Collect the report
Step 2  Ask once for anything still missing
Step 3  Create the issue
Step 4  Set type Bug, the series milestone, and the bug label
Step 5  Report the URL
```

### Step 1 — Collect

Read the stacktrace, log, or notes. Fill only what the source actually says.

| Field | Where it goes |
|-------|----------------|
| Odoo version | Body, and the series used as the milestone (`19.0` from `19.0+e` or `19.0.1`) |
| Module | `mod:` label when a single addon is clear. Otherwise omit it |
| User and group | Body |
| Steps the user was performing | Body |
| Expected result | Body |
| Result obtained | Body. Put the traceback or error here |
| Additional info the user supplied, or that you asked for and they supplied | Body |

Do not invent a user, a group, steps, an expected result, or a result. Do not paste passwords, tokens, or session cookies. Summarize a long log; keep the traceback.

### Step 2 — Ask once

If the repository, the Odoo version, the user and group, the steps, the expected result, or the result obtained is missing, ask for those items in one message. Wait. Do not open the issue yet.

### Step 3 — Create

Title: one line, the symptom. Use `gh api`, not `gh issue create`.

```bash
gh api -X POST "repos/OCA/$repo/issues" --input /tmp/odoo-report-issue.json
```

`/tmp/odoo-report-issue.json` is `{"title":"...","body":"..."}`. Body:

```markdown
## Odoo version

## User and group

## Steps

## Expected result

## Result obtained

## Additional info
```

Leave a section as `None supplied` only when the user confirmed they have nothing more for it.

### Step 4 — Milestone and bug label

`$target_ver` is the series (`19.0`). Create that milestone open if it does not exist. Set type `Bug`. Add label `bug`. When the series or the module is known, also add `series:$target_ver` and `mod:$module`. Do not set assignees. Only [odoo-assign](../odoo-assign/SKILL.md) does that.

```bash
MILESTONE_NUM=$(gh api "repos/OCA/$repo/milestones" --paginate \
  --jq ".[] | select(.title==\"$target_ver\") | .number")
if [ -z "$MILESTONE_NUM" ]; then
  MILESTONE_NUM=$(gh api -X POST "repos/OCA/$repo/milestones" \
    -f title="$target_ver" -f state=open --jq .number)
fi
gh api -X PATCH "repos/OCA/$repo/issues/$ISSUE_NUMBER" \
  -f type=Bug -F milestone="$MILESTONE_NUM"

gh api -X POST "repos/OCA/$repo/labels" \
  -f name="bug" -f color="D73A4A" -f description="Something is not working" || true
gh api -X POST "repos/OCA/$repo/issues/$ISSUE_NUMBER/labels" -f 'labels[]=bug'

gh issue view "$ISSUE_NUMBER" --repo "OCA/$repo" \
  --json type,milestone,labels \
  --jq '{type: .type.name, milestone: .milestone.title, labels: [.labels[].name]}'
```

Fail this step if `type` is not `Bug`, the milestone title is not `$target_ver`, or `bug` is missing.

Add `series:` and `mod:` the same way [odoo-fix](../odoo-fix/SKILL.md) does when those values are known. Copy an existing `series:` color, or use `1D76DB`. `mod:` is `5319E7`.

### Step 5 — Report

Issue URL, repository, series, module if known, and which sections came from the source versus from the user. Do not start a fix.
