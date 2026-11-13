# Performance review (deep review companion)

When Gate A score **≥ 40**, run a **Performance** pass in **parallel** with Bugbot and Security Review. There is no dedicated Cursor performance subagent — use Task with `subagent_type: generalPurpose` (or equivalent) and the prompt below. Retry once if the agent fails to see the diff.

## Launch prompt

```text
Full Repository Path: $WORKDIR
Diff: branch changes
Base Branch: $BASE_BRANCH

You are reviewing an Odoo/OCA addon PR for **performance only** (not correctness bugs or security).

Prefer findings in $module/ (and closely related addons in the same PR).

Inspect the PR diff and report only material performance risks:

1. N+1: `search` / `browse` / `create` / `write` / `exists` inside loops over potentially large recordsets without `mapped` / prefetch / batching
2. Unbounded searches (missing domains, no limit where a limit is appropriate) on hot paths
3. Heavy work in `onchange` that belongs in create/write, cron, or a button
4. Missing batching where the diff introduces multi-record create/write flows
5. Unnecessary `invalidate_recordset` / `flush` / `recompute` in loops
6. Stored compute / related fields that will recompute too often, or non-stored computes used in hot list/search paths without need
7. ORM patterns that scale poorly for typical FSM/sale/stock volumes (orders, lines, pickings, moves)

Severity:
- must-fix: likely real cost on normal production volumes
- suggestion: theoretical or niche / large-dataset only

Return a short bullet list. If nothing material, say "No material performance issues."
Do not repeat generic checklist items with no evidence in the diff.
```

## How to use findings

- Map **must-fix** items into the posted review’s Must fix checklist.
- Map lighter items into Suggestions.
- Still skim [checklist.md](checklist.md) § Performance yourself; the subagent does not replace judgment on false positives.
