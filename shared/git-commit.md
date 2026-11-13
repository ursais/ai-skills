# Git commit trailers (shared)

Applies to **every** `git commit` made while following any skill in this repo (module work, release init, skill-repo edits, etc.).

## Assisted-by — not Co-authored-by

**Never** add Cursor (or any Cursor agent identity) as `Co-authored-by` on a commit.

**Do** credit Cursor with an `Assisted-by` trailer instead:

```text
Assisted-by: Cursor <cursoragent@cursor.com>
```

### Required commit shape

```bash
git commit -m "$(cat <<'EOF'
<subject line>

Assisted-by: Cursor <cursoragent@cursor.com>
EOF
)"
```

### Forbidden

```bash
# Never:
git commit --trailer "Co-authored-by: Cursor <cursoragent@cursor.com>" …
# Never put Co-authored-by: Cursor … in the commit message body
```

If the environment or a hook injects `Co-authored-by: Cursor …`, **fix it automatically — never ask**:

1. Right after `git commit` (and after any amend), run `git log -1 --format=%B` and check for `Co-authored-by: Cursor`.
2. If present, rewrite HEAD so the subject/body stay the same but that trailer becomes `Assisted-by: Cursor <cursoragent@cursor.com>` (no duplicate Assisted-by). Prefer `git commit-tree` + `git reset --soft` when a normal `git commit --amend` re-injects `Co-authored-by` (Cursor often appends it after amend).
3. If that commit was already pushed on a **feature branch**, `git push --force-with-lease` immediately. Do not force-push `main`/`master`.
4. Only rewrite commits created in this conversation (or the injection on the commit you just made).

Example strip via plumbing (parents/tree from current HEAD):

```bash
TREE=$(git rev-parse 'HEAD^{tree}')
# root commit: omit -p; otherwise:
PARENT=$(git rev-parse 'HEAD^')
NEW=$(git commit-tree "$TREE" -p "$PARENT" -m "$(cat <<'EOF'
<subject>

<body if any>

Assisted-by: Cursor <cursoragent@cursor.com>
EOF
)")
git reset --soft "$NEW"
```

Human co-authors (real people) may still use standard `Co-authored-by:` when appropriate — this ban is for **Cursor / cursoragent** only.
