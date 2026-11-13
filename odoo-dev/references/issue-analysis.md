# Issue or design-document analysis

Turn the input into an implementable module specification **before** writing code.

The input is a GitHub issue **or** a design document (local `.docx` or a SharePoint URL). Use the same checklist either way. Do not generate the Word file.

## Design document

Read the `.docx` (pandoc to text is enough) or the SharePoint file the user linked. Fill the checklist from that text. Ask for `$repo`, `$module`, and `$target_ver` when they are not in the document. Skip the issue-comment steps.

## Fetch and extract (GitHub issue only)

```bash
ISSUE_JSON=$(gh issue view "$ISSUE_NUMBER" --repo "$ISSUE_OWNER/$ISSUE_REPO" \
  --json title,body,labels,milestone,comments)

echo "$ISSUE_JSON" | jq -r '.title, .body'
```

| Field | Where to look |
|-------|----------------|
| `$repo` | URL: `OCA/management-system` → `management-system` |
| `$target_ver` | Milestone title (`19.0`) or label `series:19.0` |
| `$module` | Label `mod:foo`, title `[foo]`, or proposed technical name |
| Feature scope | Issue body: user stories, acceptance criteria, mockups |
| Dependencies | Mentioned addons or related issues/PRs |

## Propose module technical name

If not stated in the issue:

1. Use repo prefix convention (`mgmtsystem_*`, `account_*`, `stock_*`, …)
2. Short, lowercase, underscores only — matches folder name
3. Confirm with user if ambiguous

```bash
ls origin/$target_ver 2>/dev/null | head -10   # after clone — inspect naming patterns
```

## Requirements checklist

Copy and fill before Step 3:

```
Source: $issue_url or design document (Word / SharePoint)
Module: $module
Target: $target_ver

Functional:
- [ ] Primary user goal:
- [ ] Models / entities:
- [ ] UI surfaces (menus, forms, wizards):
- [ ] Automation (cron, mail, server actions):
- [ ] Reports:

Technical:
- [ ] depends: [list]
- [ ] Security groups / access rights:
- [ ] Multi-company? 
- [ ] Mail / chatter integration?
- [ ] Demo data needed?

Out of scope (explicit):
- …

Reference module on $target_ver:
- …
```

## Red flags — stop and ask

| Signal | Action |
|--------|--------|
| Issue asks to change an **existing** module | Use **odoo-fix** or extend — not greenfield |
| Multiple unrelated addons in one issue | Ask to split issues; **one module per branch** |
| Depends on addon not on `$target_ver` | Note PRs; apply `blocked by dependency` via [shared/oca-pr.md](../../shared/oca-pr.md) |
| Issue is a migration request | Use **odoo-migrate** |
| No acceptance criteria | GitHub issue: comment the proposed scope and wait. Design document: ask the user |

## Link related work

Search open PRs/issues for dependencies:

```bash
gh pr list --repo "OCA/$repo" --state open --search "$module"
gh issue list --repo "OCA/$repo" --state open --label "mod:some_dependency"
```

Document links in the technical spec and in the PR body **## Dependencies** section.
