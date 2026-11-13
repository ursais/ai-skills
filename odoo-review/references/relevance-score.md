# Relevance score (Gate A)

Before a deep review, score how relevant the PR is to the OCA backlog and this repo’s users. Use a **0–100 relevance score** — never post blunt “worth reviewing: yes/no” (reads as rude).

Do **not** run Bugbot / Security / Performance, do **not** assign anyone for human testing, and do **not** spend human QA cycles when the score is in the **stop** band.

## How to score

Estimate three factors (about 0–33 each), then sum and round to a multiple of **5** (avoid fake precision like 73 vs 74):

| Factor | High when… | Low when… |
|--------|------------|-----------|
| **User / OCA value** | Clear bug fix, migration, or reusable feature | Noise, dead dump, no reusable story |
| **Novelty vs backlog** | Not already solved on `$BASE_BRANCH` / merged PRs | Duplicate or superseded |
| **Repo fit** | Belongs in this OCA repo / module set | Wrong repo, pure customer one-off |

State a one-line rationale for the score (and link duplicates when relevant).

## Bands → behavior

| Score | Band | Public wording | Action |
|------:|------|----------------|--------|
| **0–39** | Low relevance | “Relevance score: N/100 (low)” | Soft triage **COMMENT** only; stop deep review |
| **40–69** | Medium relevance | “Relevance score: N/100 (medium)” | Continue with caveats; **no** human-test assign until stronger |
| **70–100** | High relevance | “Relevance score: N/100 (high)” | Full packaging + deep review path |

**Draft / WIP** (“do not review yet”): score optionally, but **defer** deep review — comment politely; no Bugbot / Security / Performance / assign.

### Typical anchors

| Situation | Score band |
|-----------|------------|
| Spam / empty / unusable | 0–15 |
| Clear duplicate of open or merged PR | 10–30 (link the other PR) |
| Already on `$BASE_BRANCH` | 10–25 |
| Customer-only hack, weak OCA story | 25–40 |
| Overlaps another PR but still distinct | 45–65 + note the relation |
| Solid bugfix / MIG / useful optional feature | 75–95 |
| Critical widely used fix, clear test plan | 90–100 |

## Search for duplicates / overlap

```bash
gh pr list --repo "$OWNER/$repo" --state open --limit 50 \
  --json number,title,url,author,labels \
  --jq ".[] | select(.number != $PR_NUMBER)"

gh pr list --repo "$OWNER/$repo" --state all --limit 30 \
  --search "$module OR \"$(echo "$PR_TITLE" | cut -c1-40)\"" \
  --json number,title,url,state,closedAt

gh pr view "$PR_NUMBER" --repo "$OWNER/$repo" --json body,title
```

Also skim modules on the base branch for the same feature (`rg` / `git ls-tree origin/$BASE_BRANCH`).

## If score 0–39 (stop)

Post a **COMMENT** with respectful tone:

```markdown
## Triage

**Relevance score:** 25/100 (low) — …brief neutral reason…

This looks very close to … / may already be covered by … / may fit better as …

**Suggested next step:** close in favor of #N / rebase onto … / generalize for OCA by …
```

Do **not** assign `$human_tester`. Prefer helping the author over rejecting them.

## If score 40–100

Continue: packaging (labels + milestone) → technical review → human-test readiness.  
Include **Relevance score: N/100 (medium|high)** in the review summary. Medium scores should mention caveats (overlap, scope) under Notes or Suggestions.
