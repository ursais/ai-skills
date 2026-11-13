---
name: odoo-review
description: >
  Review an Odoo/OCA pull request: score relevance 0–100 (duplicates, usefulness, repo fit);
  if score ≥40, set labels/milestone and decide if ready for human testing — otherwise post a
  contributor fix checklist; when ready, assign the human tester from the contributor profile. Also checks OCA conventions, CI,
  bugs, security, performance, migration scripts, and architecture. Use when reviewing an
  OCA module PR or /odoo-review. Not for writing modules (odoo-dev), migrations
  (odoo-migrate), fixes (odoo-fix), merging (odoo-merge), rebasing (odoo-rebase), or the
  team queue report (pr-review-report).
---

# Odoo Module Review

Review `$pr_url` in **three gates**: relevance score → packaging + technical readiness → assign for human test only when ready.

**Profile:** [contributor](../shared/contributor.md). `$human_tester` is `human_tester`, or `gh api user -q .login` when that field is blank.

**Platform (shared):** [oca-conventions](../shared/oca-conventions.md) · [oca-pr](../shared/oca-pr.md) · [oca-merge-policy](../shared/oca-merge-policy.md) · [git-one-module](../shared/git-one-module.md) · [git-commit](../shared/git-commit.md) · [validation-gate](../shared/validation-gate.md) · [testing](../shared/testing.md)

## Invocation

```
/odoo-review https://github.com/OCA/field-service/pull/1234
/odoo-review OCA/field-service#1234
```

Ask for `$pr_url` if missing. Requires `gh` authenticated with permission to review/label/assign.

## Workflow

```
Step 0  Parse PR (+ checkout only if relevance ≥ 40)
Step 1  Gate A — Relevance score 0–100 (usefulness, duplicates, repo fit)
        └─ 0–39  → soft triage COMMENT, stop (no human-test assign)
Step 2  Gate B — Score ≥ 40: set labels + milestone
Step 3  Technical review (architecture, conventions, migration, CI, Bugbot, security, perf)
        Wait until those agents return. Do not post while they are running.
Step 4  Gate C — Ready for human review/testing?
        Then one review: the final decision. No second comment.
        ├─ No  → REQUEST_CHANGES (short must-fix ask) + needs fixing; do not assign for test
        └─ Yes → assign $human_tester (if free) + post review that it is ready for human test
Step 5  Report to user
```

Do **not** push code fixes unless the user explicitly asks — this skill reviews and comments only.

**Tone (GitHub vs chat):** posted reviews follow [references/review-tone.md](references/review-tone.md) — short, peer OCA voice. Never write “worth reviewing: no/yes”. Relevance score, Gate C, and CI status stay in the **user report** (and soft triage when score is low).

### Posted review body (required)

The GitHub review body is only a short ### Left to fix checklist. Do not post the long write-up with a relevance score, a CI recap, or a packaging essay.
Do not repeat a point another reviewer already raised. If your earlier review already has that checklist, check off what is done instead of posting again.
When items remain, do all of this once, in the same step: set the milestone to the target series (14.0, 19.0, …), add the needs fixing label, and submit the review as Changes requested.
If the user says not to post, return that same checklist in the chat and do not change the pull request.

### One post, at the end

Submit the GitHub review **once**, after Gate C is decided and every deep-review agent for that PR has returned or failed its one retry. That submission is the final decision (`APPROVE` or `REQUEST_CHANGES`). Do not post a provisional LGTM and correct it later.

In one run, **one review** per PR. Do not also post an issue comment. Do not approve and then request changes. GitHub cannot delete a submitted review (`deletePullRequestReview` only works on a pending review). Dismissing an approval leaves the LGTM text on the PR.

If this run already submitted a review, stop. Put any later finding in the user report only. Do not post a second review or comment to correct it.

A **later** run that re-reviews an existing checklist edits that review body (check off done items, add only new remaining items). It does not submit a second review and does not also comment.

Labels and the milestone (Gate B) are not the review; they may be set before it. Assign `$human_tester` only together with the final ready decision, never before the agents return.

## Core rules

1. **Gate A first** — score relevance; deep-review only if **≥ 40** ([references/relevance-score.md](references/relevance-score.md))  
2. When posting: one GitHub **review** at the end of the run, with the final decision — never a comment plus a review, and never an approval followed by request-changes; if **not to post**, chat-only checklist and no PR changes  
3. PRs with score **≥ 40** get packaging triage: `needs review`, `series:$target_ver`, `mod:$module`, **milestone `$target_ver`** — never skip milestone ([oca-pr](../shared/oca-pr.md))  
4. `$target_ver` = PR `baseRefName`  
5. **Assign `$human_tester` only when Gate C passes** and the PR has **no other assignee**; never steal an existing assignee  
6. If items remain → **once, same step**: milestone `$target_ver` + `needs fixing` + `REQUEST_CHANGES` with `### Left to fix` only; **do not** assign `$human_tester` for testing  
7. Architecture of the *solution* still applies when Gate A continues ([references/architecture-relevance.md](references/architecture-relevance.md))  
8. Migration script need, Bugbot, Security Review, and Performance pass when doing a deep review  



## Step 0 — Inputs

```bash
[ -z "$(gh auth token 2>/dev/null)" ] && echo "ERROR: gh not authenticated" && exit 1

gh pr view "$PR_NUMBER" --repo "$OWNER/$repo" \
  --json title,body,author,baseRefName,headRefName,headRepository,files,labels,assignees,commits,url,isDraft
```

`$BASE_BRANCH` / `$target_ver` = `baseRefName`. Identify `$module` from changed addon dirs when possible.

Defer local checkout / Bugbot / Security / Performance until relevance **≥ 40**.

## Step 1 — Gate A: relevance score

Follow [references/relevance-score.md](references/relevance-score.md).

Compute **Relevance score (0–100)** from user/OCA value, novelty vs backlog, and repo fit. Round to a multiple of 5. Record band: low (0–39) / medium (40–69) / high (70–100).

**If 0–39 (or defer WIP):**

```bash
gh api --method POST "repos/$OWNER/$repo/pulls/$PR_NUMBER/reviews" --input - <<EOF
{"event":"COMMENT","body":"## Triage\n\n**Relevance score:** 25/100 (low) — …neutral reason…\n\n**Suggested next step:** …"}
EOF
```

Stop. Report to the user. **Do not** assign `$human_tester`.

**If ≥ 40:** continue (mention medium-score caveats in Notes when 40–69).

## Step 2 — Gate B: packaging (score ≥ 40)

Set labels + milestone now ([oca-pr](../shared/oca-pr.md)):

```bash
target_ver="$BASE_BRANCH"
MILESTONE_NUM=$(gh api "repos/$OWNER/$repo/milestones" --paginate \
  --jq ".[] | select(.title==\"$target_ver\") | .number")
if [ -z "$MILESTONE_NUM" ]; then
  MILESTONE_NUM=$(gh api -X POST "repos/$OWNER/$repo/milestones" \
    -f title="$target_ver" -f state=open --jq .number)
fi
gh api -X PATCH "repos/$OWNER/$repo/issues/$PR_NUMBER" -F milestone="$MILESTONE_NUM"

gh api -X POST "repos/$OWNER/$repo/issues/$PR_NUMBER/labels" \
  -f 'labels[]=needs review' \
  -f "labels[]=series:${target_ver}" \
  -f "labels[]=mod:${module}" || true

gh pr view "$PR_NUMBER" --repo "$OWNER/$repo" --json milestone \
  --jq '.milestone.title // empty' | grep -qx "$target_ver" \
  || { echo "ERROR: milestone $target_ver not set"; exit 1; }
```

Do **not** assign `$human_tester` here — assignment is Gate C only.

## Step 3 — Technical review (deep)

Checkout PR head when needed:

```bash
WORKDIR=/tmp/oca-review/${OWNER}-${repo}-${PR_NUMBER}
mkdir -p /tmp/oca-review && cd /tmp/oca-review
gh pr checkout "$PR_NUMBER" --repo "$OWNER/$repo" \
  || { git clone "https://github.com/$OWNER/$repo.git" "$WORKDIR" && cd "$WORKDIR" && gh pr checkout "$PR_NUMBER"; }
```

Run all of:

| Check | Reference |
|-------|-----------|
| CI | `gh pr checks` — red/pending → not ready for human test |
| Architecture / solution shape | [architecture-relevance.md](references/architecture-relevance.md) |
| OCA conventions + coding standards | [checklist.md](references/checklist.md), [oca-conventions](../shared/oca-conventions.md) |
| Migration script need | [migration-needed.md](references/migration-needed.md) |
| Bugbot + Security + Performance | **three parallel** agents; retry each once |

One-module preference: [git-one-module](../shared/git-one-module.md).

### Bugbot / Security / Performance (required when score ≥ 40)

Launch **in the same turn** (parallel):

1. **Bugbot** (`subagent_type: bugbot`)
2. **Security Review** (`subagent_type: security-review`)
3. **Performance** (`subagent_type: generalPurpose`) — prompt in [performance-review.md](references/performance-review.md)

Bugbot / Security:

```text
Full Repository Path: $WORKDIR
Diff: branch changes
Base Branch: $BASE_BRANCH
Custom Instructions: Odoo/OCA addon PR. Prefer findings in $module/.
```

(Security: also flag ACL/`sudo()`/SQL/`safe_eval`/public controllers/QWeb XSS.)

The checkout must contain `origin/$BASE_BRANCH` before those agents start. A detached worktree without that ref cannot compute `branch changes`. Fetch the base, then retry a failed diff **once**. A failed diff is not a pass.

**Do not post the GitHub review in the turn that launches the agents.** Wait until they finish, fold must-fix findings into the one checklist, then submit. A batch of PRs is the same rule per PR: no review for a PR whose agents are still running.

Performance: use the full prompt from [performance-review.md](references/performance-review.md) (N+1, unbounded search, onchange cost, batching, flush/invalidate, compute scaling). Fold must-fix findings into the contributor checklist; suggestions stay under Suggestions. Series pitfalls (wrong `create`, removed fields, company rules, `sudo` scope, groups on buttons) are in [checklist.md](references/checklist.md).

## Step 4 — Gate C: ready for human review/testing?

**Ready for human testing** only if **all** are true:

- Relevance score **≥ 40** (prefer **≥ 70** before assigning scarce human time; for **40–69** assign only if the user explicitly wants)
- CI green (or only out-of-scope codecov/project red)
- No **must-fix** left
- **Human-test path documented** — see below (not “PR Test scenario always”)
- Not draft

### Human-test path (docs first)

Testers should follow **product docs**, not a one-off PR recipe. Prefer `readme/USAGE.md` (and CONFIGURE when needed).

| Change | Gate C expectation |
|--------|-------------------|
| Fix / IMP of a flow **already** in USAGE | Docs + CI/tests enough; do **not** block on missing PR `## Test scenario` |
| New or changed **user-visible** behavior | **USAGE updated in the PR** (preferred). PR `## Test scenario` only if docs are not updated yet |
| New module / greenfield feature | USAGE required; PR Test scenario OK until docs exist |

**Must-fix** when the path a human must exercise is covered by **neither** updated USAGE/CONFIGURE **nor** a concrete PR `## Test scenario`. Ask for USAGE first when the gap is lasting product behavior; ask for a PR Test scenario only as a temporary handoff.

Do **not** fail Gate C solely because the PR body lacks `## Test scenario` when USAGE already describes the flow.

For **tiny forward-ports / obvious bugfixes**, do **not** block on USAGE/Test scenario on GitHub — note it in the user report only if useful. Reserve the public ask for new lasting product behavior.

### Not ready → request changes (short)

Build `/tmp/oca-review-body.json` as a short `### Left to fix` checklist only ([review-tone.md](references/review-tone.md)). No scorecard, CI recap, or packaging essay.

If **a previous run** already posted that checklist: `PUT` the same review (check off done items, add only new remaining items). Do **not** submit another review and do **not** also comment. Skip points another reviewer already raised.

If **this run** already submitted a review, do not post again. See [One post, at the end](#one-post-at-the-end).

When items remain and nothing has been submitted yet, **once**: set milestone `$target_ver`, add `needs fixing`, submit **one** `REQUEST_CHANGES` review.

```bash
# milestone (idempotent) + needs fixing + single REQUEST_CHANGES review
gh api -X PATCH "repos/$OWNER/$repo/issues/$PR_NUMBER" -F milestone="$MILESTONE_NUM"
gh api -X POST "repos/$OWNER/$repo/issues/$PR_NUMBER/labels" -f 'labels[]=needs fixing' || true
gh api --method POST "repos/$OWNER/$repo/pulls/$PR_NUMBER/reviews" --input /tmp/oca-review-body.json
```

**Do not** assign `$human_tester`. Keep `needs review` + `needs fixing`.

If the user says **not to post**: return that same `### Left to fix` checklist in chat and **do not** change the pull request.

### Ready → assign for human test

```bash
HUMAN_TESTER="${human_tester:-$(gh api user -q .login)}"
existing=$(gh pr view "$PR_NUMBER" --repo "$OWNER/$repo" \
  --json assignees --jq '[.assignees[].login] | join(",")')
if [ -z "$existing" ]; then
  gh api -X POST "repos/$OWNER/$repo/issues/$PR_NUMBER/assignees" \
    -f "assignees[]=${HUMAN_TESTER}"
elif echo ",$existing," | grep -qv ",${HUMAN_TESTER},"; then
  echo "NOTE: already assigned to $existing — leave as-is (do not steal)"
fi
gh api -X POST "repos/$OWNER/$repo/pulls/$PR_NUMBER/requested_reviewers" \
  -f "reviewers[]=${HUMAN_TESTER}" || true
```

| Gate C | `event` |
|--------|---------|
| Not ready (must-fix) | `REQUEST_CHANGES` |
| Ready, only nits you care about | `COMMENT` or `APPROVE` (omit nits on GitHub by default) |
| Ready, clean | `APPROVE` |

Track **Ready for human review/testing:** yes/no in the user report only.

### Review body (GitHub)

The GitHub review body is only a short ### Left to fix checklist. Do not post the long write-up with a relevance score, a CI recap, or a packaging essay.

Fold must-fix agent findings into that checklist. Keep nice-to-haves out of the PR unless the user wants them. Approve bodies stay minimal (`LGTM`) per [review-tone.md](references/review-tone.md).

## Step 5 — Report to user

In **chat** (internal scorecard OK here): PR link; relevance score + band; Gate B/C; labels/milestone; must-fix vs assigned to **$human_tester**; review URL.

If the user said not to post, the chat **is** the `### Left to fix` checklist (same content you would have submitted).

## Skill-specific references

| File | Contents |
|------|----------|
| [references/relevance-score.md](references/relevance-score.md) | 0–100 score, bands, soft triage tone — Gate A |
| [references/review-tone.md](references/review-tone.md) | Short OCA peer voice on GitHub; what stays internal |
| [references/architecture-relevance.md](references/architecture-relevance.md) | Solution shape / module placement |
| [references/migration-needed.md](references/migration-needed.md) | When a migration script is required |
| [references/performance-review.md](references/performance-review.md) | Parallel performance agent prompt + how to fold findings |
| [references/checklist.md](references/checklist.md) | Conventions, security, performance, architecture bullets |
