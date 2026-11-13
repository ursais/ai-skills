# ursais Remote (shared)

**Push to ursais, never to OCA.**

- `origin` = `OCA/$repo` — fetch/checkout only
- `ursais` = `ursais/$repo` — all pushes

## Prerequisites

```bash
[ -z "$GITHUB_TOKEN" ] && echo "ERROR: GITHUB_TOKEN not set" && exit 1
```

Token needs `repo` scope.

## Add remote and push

```bash
# Create fork if missing
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/ursais/$repo" | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(d.get('full_name','MISSING'))" \
  | grep -q ursais || {
    curl -s -X POST -H "Authorization: token $GITHUB_TOKEN" \
      "https://api.github.com/repos/OCA/$repo/forks" \
      -d '{"organization":"ursais"}'
    sleep 30
  }

git remote add ursais "https://${GITHUB_TOKEN}@github.com/ursais/${repo}.git" 2>/dev/null || true
git push -u ursais "$BRANCH"
```

Never `git push origin` on workflow branches.
