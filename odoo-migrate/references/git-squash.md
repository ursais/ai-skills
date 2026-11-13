# Squash Consecutive Same-Author Commits

Apply after `git am`, **before** migration commits. Scope: `origin/$target_ver..HEAD` only.

**Prerequisite:** `format-patch` must use `-- $module` ([git-one-module.md](../../shared/git-one-module.md)).

## What this is NOT

- **Not** a single-commit migration — never `git reset --soft` + one commit for the whole PR
- **Not** squashing ADD / UPD pot / README / IMP / MIG into one commit
- Preserve the rebased commit chain; only collapse **consecutive same-author duplicates**

## Rules

- Squash only **consecutive** commits with the same author email (`%ae`)
- Do **not** reorder commits on the first pass
- Keep the first message in each run (`pick`); mark later ones `fixup`
- On conflict: `git rebase --abort`, retry manually with fewer fixups, or skip and note in report

Reference: [OCA maintainer-tools — Merge/squash commits](https://github.com/OCA/maintainer-tools/wiki/Merge-commits-in-pull-requests#mergesquash-the-commits-generated-by-bots-or-weblate)

## Automated (preferred)

```bash
cd /tmp/oca-mig/$repo/$repo
BASE="origin/$target_ver"
COUNT=$(git rev-list --count "$BASE"..HEAD)
if [ "$COUNT" -le 1 ]; then
  echo "Nothing to squash ($COUNT commit)"
else
  SCRIPT="$(dirname "$0")/../scripts/squash-same-author.py"
  GIT_SEQUENCE_EDITOR="python3 $SCRIPT" git rebase -i "$BASE"
fi
git log --oneline "$BASE"..HEAD
```

Report before → after commit count (e.g. "28 → 14").

## Manual fallback

```bash
git config rebase.instructionFormat "(%an) %s"
git rebase -i "origin/$target_ver"
# Change pick → fixup for consecutive same-author commits
```
