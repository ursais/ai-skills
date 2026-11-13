# One Module Per Branch (shared)

**Hard rule for all write skills:** one addon directory per branch and PR.

## Branch naming

| Skill | Branch pattern |
|-------|----------------|
| odoo-module-migrate | `${target_ver}-mig-$module` |
| odoo-module-dev | `${target_ver}-add-${module}-${ISSUE_NUMBER}` |
| odoo-module-fix | `${target_ver}-fix-${module}-${ISSUE_NUMBER}` |

Never combine modules in one branch name or PR.

## Staging

- Stage only `$module/` — never `git add -A` or `git add .` on OCA workflow branches
- If work needs another addon → separate branch + PR

## Verify before commit / push / PR

```bash
changed_addons() {
  git diff --name-only "origin/${target_ver}"...HEAD \
    | awk -F/ 'NF>1{print $1}' | sort -u \
    | while read d; do [ -f "$d/__manifest__.py" ] && echo "$d"; done
}

CHANGED=$(changed_addons)
if [ "$CHANGED" != "$module" ]; then
  echo "ERROR: branch must touch only $module — found: ${CHANGED:-<none>}"
  exit 1
fi
```

## Migration-specific: `format-patch` scope

```bash
git format-patch --keep-subject --stdout origin/$target_ver..origin/$source_ver -- $module \
  | git am -3 --keep
```

**The `-- $module` suffix is mandatory** — without it, `git am` imports the entire repo history.
