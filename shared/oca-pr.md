# OCA PR Packaging and CI (shared)

Used after local validation and push to `$fork_owner` ([fork-remote.md](fork-remote.md)). Verify [git-one-module.md](git-one-module.md) first. `$fork_owner` comes from [contributor.md](contributor.md).

## Standard labels

| Always (never skip) | Optional |
|---------------------|----------|
| **`needs review`** (API POST) | `blocked by dependency` when unmerged deps |
| **Milestone `$target_ver`** (title = series / PR `baseRefName`) | Workflow-specific: `migration`, `bug` |
| `series:${target_ver}` | **`needs fixing`** when requesting changes (keep `needs review`) |
| `mod:${module}` only | |

Existing `series:` / `mod:` labels do **not** skip this. Still set the milestone and add `needs review` when they are missing.

Do not set assignees. Only [odoo-assign](../odoo-assign/SKILL.md) does that.  
Reviewer: `$PR_REVIEWER` (profile `maintainer`, otherwise `gh api user -q .login`).

Use **`gh api` REST**, not `gh pr edit` — `gh pr edit` can fail on the Projects Classic GraphQL deprecation (including for milestones).

Create missing labels before POSTing them (`mod:$module`, `needs fixing`, …). Match sibling label color when possible (`mod:` is `5319E7`; `needs fixing` is `D93F0B`).

If the `$target_ver` milestone does not exist, **create** it (open), then set it on the pull request. Verify after PATCH that `.milestone.title == $target_ver`.

```bash
PR_REVIEWER="${PR_REVIEWER:-${maintainer:-$(gh api user -q .login)}}"

# Milestone — required; title must equal $target_ver (e.g. 19.0)
MILESTONE_NUM=$(gh api "repos/OCA/$repo/milestones" --paginate \
  --jq ".[] | select(.title==\"$target_ver\") | .number")
if [ -z "$MILESTONE_NUM" ]; then
  MILESTONE_NUM=$(gh api -X POST "repos/OCA/$repo/milestones" \
    -f title="$target_ver" -f state=open --jq .number)
fi
gh api -X PATCH "repos/OCA/$repo/issues/$PR_NUMBER" \
  -F milestone="$MILESTONE_NUM"

gh api -X POST "repos/OCA/$repo/issues/$PR_NUMBER/labels" \
  -f 'labels[]=needs review' \
  -f "labels[]=series:${target_ver}" \
  -f "labels[]=mod:${module}"
# Plus workflow labels, e.g. -f 'labels[]=migration' or -f 'labels[]=bug'

gh pr view "$PR_NUMBER" --repo "OCA/$repo" --json labels \
  --jq '[.labels[].name] | index("needs review") // empty' \
  | grep -q . || gh api -X POST "repos/OCA/$repo/issues/$PR_NUMBER/labels" -f 'labels[]=needs review'

# Fail the packaging step if milestone is still missing
gh pr view "$PR_NUMBER" --repo "OCA/$repo" --json milestone \
  --jq '.milestone.title // empty' | grep -qx "$target_ver" \
  || { echo "ERROR: milestone $target_ver not set on #$PR_NUMBER"; exit 1; }

gh api -X POST "repos/OCA/$repo/pulls/$PR_NUMBER/requested_reviewers" \
  -f "reviewers[]=${PR_REVIEWER}"
```

## Unmerged dependencies

A dep is pending when it is not on `origin/$target_ver`. List them in the PR **body** under
**## Dependencies** — do **not** post a separate Dependencies comment.

```bash
eval "$(python3 <<PY
import ast, pathlib, re, subprocess
repo, target_ver, module = "$repo", "$target_ver", "$module"
core = {"base","web","mail","uom","account","sale","purchase","stock","fleet","hr","product","contacts"}
src = pathlib.Path(module, "__manifest__.py").read_text()
data = ast.literal_eval(re.search(r"\{.*\}", src, re.S).group())
deps = [d for d in data.get("depends", []) if d not in core]
pending, lines = [], []
for dep in deps:
    r = subprocess.run(["git", "cat-file", "-e", f"origin/{target_ver}:{dep}/__manifest__.py"], capture_output=True)
    if r.returncode == 0: continue
    pending.append(dep)
    pr = subprocess.run(
        ["gh","pr","list","--repo",f"OCA/{repo}","--state","open",
         "--search",f"[{target_ver}][MIG] {dep}","--json","number,title,url",
         "--jq",'.[0] | select(. != null) | "- [#\\(.number)](\\(.url)) \\(.title)"'],
        capture_output=True, text=True)
    lines.append(pr.stdout.strip() or f"- \`{dep}\` — no open migration PR on \`OCA/{repo}\`")
text = "\n".join(lines) if lines else f"All manifest dependencies are already on \`{target_ver}\`."
print(f"export HAS_UNMERGED_DEPS={'true' if pending else 'false'}")
print("export DEP_LINES=\$(cat <<'EOF'")
print(text)
print("EOF")
print(")")
PY
)"

if [ "$HAS_UNMERGED_DEPS" = true ]; then
  BLOCK_LABEL=$(gh api "repos/OCA/$repo/labels" --paginate --jq '.[].name' \
    | grep -iE '^blocked by dependenc' | head -1)
  BLOCK_LABEL="${BLOCK_LABEL:-blocked by dependency}"
  gh api -X POST "repos/OCA/$repo/issues/$PR_NUMBER/labels" -f "labels[]=${BLOCK_LABEL}"
fi
```

## Create PR (template)

```bash
PR_URL=$(gh pr create --repo "OCA/$repo" \
  --head "${fork_owner}:${BRANCH}" \
  --base "$target_ver" \
  --title "$PR_TITLE" \
  --body "$PR_BODY")
PR_NUMBER=${PR_URL##*/}
```

### PR body (description — required sections)

`$PR_BODY` is the PR **description** (GitHub’s first/main body). Always include:

1. **Human-test path** — prefer product docs; see below
2. **## Dependencies** — with `$DEP_LINES` (or “all deps on `$target_ver`”)
3. Summary / changes / validation as appropriate for the workflow

**Docs first:** for user-visible fixes/IMPs, update `readme/USAGE.md` (and CONFIGURE when needed)
so a human tester can follow the module docs. Do not treat a disposable PR recipe as a substitute
for lasting documentation.

**## Test scenario** in the PR body when:

- USAGE/CONFIGURE does **not** yet cover the path the reviewer must exercise, or
- You want a short handoff that **points at** the USAGE steps (and any before/after for a bug fix)

When you include it, use concrete numbered steps (install/upgrade, menus, records, expected
results), based on what you ran locally. Example:

```markdown
## Test scenario

1. Install (or upgrade) \`$module\` on Odoo $target_ver with demo data.
2. Follow Usage in the module README (confirm SO → FSM created), then:
3. Cancel the Sale Order → linked FSM orders are cancelled/closed.
4. Set SO to draft and reconfirm → a new FSM order is created; prior cancelled ones remain linked.
5. Run: \`odoo … --test-tags=/$module\` (or note coverage % from the validation gate).
```

For bug fixes, include the **before** failure and the **after** expected result when that is not
obvious from USAGE.
For migrations, include install + upgrade smoke checks and any new API/UI paths.
For new modules, ship USAGE (configure + primary flow) and a PR Test scenario until docs exist.

When reviewing others’ PRs, Gate C in **`odoo-review`** accepts USAGE **or** a PR Test scenario —
do not block solely on a missing PR section if the readme already covers the flow.

## Comments

| Workflow | Comment |
|----------|---------|
| migration | `/ocabot migration ${module}` only |
| new module / fix | `$issue_url` |

## Triage / request changes

Full review workflow (conventions, CI, bugs, security, performance → posted GitHub review):
**`odoo-review`**.

When reviewing someone else's PR (not opening one):

1. Apply the standard labels, **milestone `$target_ver`**, and reviewer (section above) — **before** posting the GitHub review. Milestone is as mandatory as `needs review`. Do not set assignees.
2. **Manifest check (required):** every changed addon’s `__manifest__.py` must set
   **`development_status`** and **`maintainers`** (non-empty list). See [oca-conventions.md](oca-conventions.md).

```bash
# For each module directory touched by the PR:
python3 -c "
import ast, pathlib, sys
path = pathlib.Path('$module/__manifest__.py')
data = ast.literal_eval(path.read_text())
missing = []
if not data.get('development_status'):
    missing.append('development_status')
m = data.get('maintainers')
if not isinstance(m, list) or not m:
    missing.append('maintainers')
if missing:
    raise SystemExit(f'FAIL {path}: missing {chr(44).join(missing)}')
print(f'OK {path}: development_status={data[\"development_status\"]!r} maintainers={m}')
"
```

3. If the review finds problems (including missing manifest keys), **also** add `needs fixing`
   (create the label if the repo lacks it). Do not remove `needs review`.
4. Post a **Request changes** review with a checkbox list. Prefer REST:

```bash
# Create needs fixing if missing
gh api -X POST "repos/OCA/$repo/labels" \
  -f name="needs fixing" -f color="D93F0B" \
  -f description="Changes requested; author needs to fix" || true

gh api -X POST "repos/OCA/$repo/issues/$PR_NUMBER/labels" \
  -f 'labels[]=needs fixing'

# body.json → {"event":"REQUEST_CHANGES","body":"...markdown with - [ ] items..."}
gh api --method POST "repos/OCA/$repo/pulls/$PR_NUMBER/reviews" --input body.json
```

Keep `needs review` + `needs fixing` together until the author addresses the list.

## CI until green

```bash
gh pr checks "$PR_NUMBER" --repo "OCA/$repo" --watch --interval 30
```

1. Wait until all checks finish  
2. Fix **in-scope** failures locally → [validation-gate.md](validation-gate.md)  
3. One `[FIX]` commit (or amend if fix skill requires single commit) → **one push** to `fork` — trailer **`Assisted-by: Cursor`**, never `Co-authored-by: Cursor` ([git-commit.md](git-commit.md))  
4. Max 3 attempts per same failure  

| Check | Action |
|-------|--------|
| pre-commit / prettier / pylint | Fix in `$module/` |
| tests | Fix `$module/tests/` or code |
| codecov/patch | Add tests until coverage > 99% |
| codecov/project | **Out of scope** if patch is green — do not expand to other modules |
| unreleased dependencies | Fix `depends` |
| runboat/build | Fix install/runtime from Runboat log |

Merge only after [oca-merge-policy.md](oca-merge-policy.md).
