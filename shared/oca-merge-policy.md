# OCA merge policy (shared)

No skill approves a pull request. A human approves after testing. Skills may request changes or comment. They must not submit `APPROVE`.

Do **not** merge an OCA PR (`/ocabot merge`, `gh pr merge`) until **CI is green** **and** the
review/age rules below are satisfied.

**Full merge workflow** (gates + `/ocabot merge patch|minor|major` or GitHub API): **`odoo-merge`**.

## Rules

1. **Wait 5 days** after the PR was opened.
2. **2 reviews** (or **3 reviews** when required by the repo/PSG).
3. **No-review fallback**: If **nobody reviewed** within **5 days**, a maintainer may merge anyway
   (CI must still be green).
4. **Coverage**: patch coverage checks (e.g. `codecov/patch`) must be green when present; project-only
   coverage is not a blocker if patch is green.

**`odoo-merge` also requires** (stricter than the fallback above): the **assignee** (not the author) has **APPROVED after testing**. If `/ocabot merge` already aborted and there is no later commit, do not merge again.

## When reporting "ready to merge"

| Situation | Merge? |
|-----------|--------|
| CI green, ≥ 5 days, ≥ 2 approvals (or 3 if required), assignee (not author) APPROVED | Yes |
| CI green, ≥ 5 days, **zero** reviews | Only if the user explicitly asks (OCA no-review fallback). `odoo-merge` does not do this by default. |
| CI green, ≥ 5 days, only 1 approval | No — need one more review |
| Assignee has not APPROVED, or assignment is only the author | No — Test / Assign first |
| `/ocabot merge` aborted and no new commit since | No — Fix first |
| CI green, < 5 days | No — wait |
| CI red | No — fix first |

## Check with `gh`

```bash
gh pr view "$PR_NUMBER" --repo "OCA/$repo" --json createdAt,reviews,author,reviewDecision \
  --jq '{
    created: .createdAt,
    age_days: ((now - (.createdAt | fromdateiso8601)) / 86400 | floor),
    approvals: (.author.login as $a | [.reviews[] | select(.state == "APPROVED" and .author.login != $a)] | unique_by(.author.login) | length),
    review_decision: .reviewDecision
  }'
```

Never recommend merge on CI green alone without checking age, reviews, and coverage.

On OCA repos, merge by commenting `/ocabot merge patch|minor|major` (not `gh pr merge`).
On non-OCA repos, merge with the GitHub API (`gh pr merge`).
