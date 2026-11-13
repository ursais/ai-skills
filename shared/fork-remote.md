# Fork remote (shared)

Read [contributor.md](contributor.md) first. `$fork_owner` is `fork_owner`. If it is still `YOUR_GITHUB_ORG`, stop.

**Push to `$fork_owner`, never to OCA.**

- `origin` = `OCA/$repo` — fetch and checkout only
- `fork` = `$fork_owner/$repo` — all pushes

## Prerequisites

```bash
[ -z "$GITHUB_TOKEN" ] && echo "ERROR: GITHUB_TOKEN not set" && exit 1
```

Token needs `repo` scope. `$fork_owner` must already be set from the contributor profile.

## Add remote and push

```bash
owner_type=$(gh api "users/$fork_owner" --jq .type)
if ! gh repo view "$fork_owner/$repo" >/dev/null 2>&1; then
  if [ "$owner_type" = "Organization" ]; then
    gh api -X POST "repos/OCA/$repo/forks" -f organization="$fork_owner" >/dev/null
  else
    gh api -X POST "repos/OCA/$repo/forks" >/dev/null
  fi
  sleep 15
fi

git remote add fork "https://${GITHUB_TOKEN}@github.com/${fork_owner}/${repo}.git" 2>/dev/null || \
  git remote set-url fork "https://${GITHUB_TOKEN}@github.com/${fork_owner}/${repo}.git"
git push -u fork "$BRANCH"
```

Never `git push origin` on workflow branches.
