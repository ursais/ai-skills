# Step 3 — Migration Tasks

Read the version guide first (and **every intermediate** guide when jumping versions):
- 17.0 → [migration-17.0.md](migration-17.0.md)
- 18.0 → [migration-18.0.md](migration-18.0.md)
- 19.0 → [migration-19.0.md](migration-19.0.md)
- 20.0 → [migration-20.0.md](migration-20.0.md) · [OCA wiki](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-20.0)
- Other → OCA wiki `Migration-to-version-${target_ver}`

Shared polish (icon, GML, readme, headers, demo): [../../shared/oca-conventions.md](../../shared/oca-conventions.md)

## Universal checklist

1. Bump `'version': '${target_ver}.1.0.0'` in `__manifest__.py`
2. Ensure **`development_status`** and **`maintainers`** are set ([shared/oca-conventions.md](../../shared/oca-conventions.md))
3. Remove `$module/migrations/` if present
4. Do **not** change copyright years or original authors (except OSI→GML rename)
5. Apply [shared/oca-conventions.md](../../shared/oca-conventions.md) (icon, GML, readme, headers, demo split)
6. Apply version-specific framework changes from the migration guide
7. Add enough unit tests for coverage **> 99%** before `[MIG]` (below)
8. Update i18n — separate `[UPD]` commit (below)
9. Validation gate → push → CI ([../../shared/validation-gate.md](../../shared/validation-gate.md))

## Unit tests (coverage must be > 99%)

**Hard rule:** add/extend tests until local coverage on `$module/` is **> 99%** (≥ 99.08%)
**before** `[MIG]` and before every push. Part of the migration, not optional follow-up.

Gate: [../../shared/validation-gate.md](../../shared/validation-gate.md) · [../../shared/testing.md](../../shared/testing.md)

| Module shape | Action |
|--------------|--------|
| Custom models / wizards / controllers / crons | Must reach > 99% |
| Existing `$module/tests/` | Update for `$target_ver` + fill gaps |
| Thin/no tests | Create `$module/tests/` |
| Data/XML-only, no executable Python | Skip only if coverage already 100% — document |

```bash
python3 -m coverage run --source="$module" $OCA_TEST_CMD
python3 -m coverage report -m --include="*/${module}/*" --omit="*/__manifest__.py"
# add tests for Missing lines → re-run until ≥ 99.08%
git add "$module/tests/"
git commit -m "$(cat <<'EOF'
[ADD] $module: unit tests

Assisted-by: Cursor <cursoragent@cursor.com>
EOF
)"   # prefer before [MIG] if large; never Co-authored-by Cursor — see shared/git-commit.md
```

**Never** create `[MIG]` while coverage ≤ 99%.

## Translations

After `[MIG]` only — see [../../shared/oca-conventions.md](../../shared/oca-conventions.md).  
Prefer **`odoo-translate`** (Weblate for OCA; local `i18n/` otherwise).

```bash
POT="$module/i18n/${module}.pot"
MODULE_LANGS=$(ls "$module/i18n"/*.po 2>/dev/null | xargs -n1 basename | sed 's/.po$//' | grep -vx en)
REF=$(git ls-tree --name-only origin/$target_ver | while read d; do
  [ "$d" = "$module" ] && continue; [ -d "$d/i18n" ] || continue
  case "$d" in ${module%%_*}_*) echo "$d"; break ;; esac; done)
REF_LANGS=$(ls "$REF/i18n"/*.po 2>/dev/null | xargs -n1 basename | sed 's/.po$//' | grep -vx en)
I18N_LANGS=$(printf '%s\n%s\n' "$MODULE_LANGS" "$REF_LANGS" | sort -u | grep -vx en)

# prefer click-odoo-makepot; else msgmerge/msginit per lang
git add "$module/i18n/"
git commit -m "$(cat <<'EOF'
[UPD] Update ${module}.pot

Assisted-by: Cursor <cursoragent@cursor.com>
EOF
)"
```

## TODO convention

```python
# TODO [MIG] v{target_ver}: <what and why>
# Reference: <url>
```

Report all TODOs in Step 7.
