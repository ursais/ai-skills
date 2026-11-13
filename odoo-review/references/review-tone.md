# GitHub review tone (OCA)

Posted reviews must read like a **peer maintainer**, not an audit report. Formal gates stay **internal** (agent reasoning + Step 5 user report).

## Posted review body (required)

The GitHub review body is only a short ### Left to fix checklist. Do not post the long write-up with a relevance score, a CI recap, or a packaging essay.
Do not repeat a point another reviewer already raised. If your earlier review already has that checklist, check off what is done instead of posting again.
When items remain, do all of this once, at the end of the review, after Bugbot, Security, and Performance have returned: set the milestone to the target series (14.0, 19.0, …), add the needs fixing label, and submit the review as Changes requested.
One review per PR per run. That review is the final decision. Do not also post an issue comment. Do not approve and then request changes. GitHub cannot delete a submitted review (`deletePullRequestReview` only works on a pending review); dismissing an approval still leaves the LGTM text visible.
If this run already submitted a review, stop. Later findings stay in chat.
If the user says not to post, return that same checklist in the chat and do not change the pull request.

## What OCA reviewers actually write

Many reviews are one line (`LGTM`, `code review`). When requesting changes, a **short checklist** is enough. Long scorecards, “Checked” lists, and “nice to have” piles annoy contributors and get ignored.

## Public vs internal

| Put on GitHub | Keep in chat / agent only |
|---------------|---------------------------|
| `### Left to fix` checklist (open items only) | Relevance score + band |
| Minimal code snippet inside a checklist item when it saves a round-trip | “Ready for human testing: yes/no” |
| `LGTM` / thanks when approving | CI green/red (visible on the PR) |
| | Packaging essay / milestone prose / Bugbot / Security / Perf checklists |
| | Nice-to-haves unless you personally care or the user asked |

## Do / don’t

**Do**
- Sound human and brief
- Block only on real regressions, broken CI, missing migration when required, or other must-fix
- Use unchecked `- [ ]` items the author can act on
- Prefer one or two concrete asks over a dump
- Deduplicate against other reviewers and your own prior checklist

**Don’t**
- Post `## Review summary`, relevance scores, CI recaps, packaging essays, `### Checked`, or Gate A/B/C language
- Say “CI is green” / “CI looks good” — adds no info (checks are on the PR)
- List suggestions / nits by default
- Demand USAGE / Test scenario for tiny FW/bugfixes when the change is obvious to exercise
- Paste internal agent findings (Bugbot/Security/Perf) unless they are actionable must-fixes
- Post an issue comment and then a review with the same body
- Approve, then request changes in the same run. One review, after the checks finish, is the decision

## Templates

### Request changes (required shape)

```markdown
### Left to fix
- [ ] Guard missing `attribute_field_id` in `checkAttributeFieldUsage` (it’s optional) — return true when unset
- [ ] …
```

Optional one-line thanks above the heading is fine; nothing else.

### Re-review (items already on your prior checklist)

On a **later** run, edit the existing review body: check off done items (`- [x]`) and add only new `- [ ]` items. Do not submit a second review. Do not also post an issue comment. Do not change an `APPROVE` into `REQUEST_CHANGES` in the same run — wait until the decision is final before the first submit.

### Approve (clean)

```markdown
Thanks, LGTM.
```

### Approve / comment with one optional note (rare)

```markdown
LGTM — optional: …one short nit if you truly care…
```

### Low relevance triage (Gate A stop)

Stay short and neutral — still no scorecard tone beyond the required relevance line from [relevance-score.md](relevance-score.md).

## Not to post

If the user says **not to post**, return that same `### Left to fix` checklist in chat and **do not** change the pull request (no review, label, milestone, or assign).
