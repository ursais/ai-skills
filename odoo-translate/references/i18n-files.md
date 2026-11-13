# Local i18n/ file management

Use when Weblate is not the path (private modules, missing component, `.pot` prep on a branch). Conventions: [../../shared/oca-conventions.md](../../shared/oca-conventions.md).

## Layout

```text
$module/
└── i18n/
    ├── $module.pot     # template (source strings)
    ├── fr.po           # French
    ├── es.po           # Spanish
    └── es_MX.po        # optional regional
```

- **Never** add `en.po`.  
- Language codes: prefer ISO codes used by sibling OCA modules on the same series (`es`, `es_MX`, `pt_BR`, …).

## Refresh the template (`.pot`)

Prefer **click-odoo-makepot** against a DB with the module installed:

```bash
# Example — adapt to the project harness
click-odoo-makepot -d "$DB" --addons-path="$ADDONS" -m "$module" \
  --msgmerge / --commit   # or without --commit; skill commits [UPD] separately
```

If makepot is unavailable, use the project’s documented export (Odoo UI **Export Translation**, or `odoo-bin` i18n export) into `$module/i18n/${module}.pot`.

## Update existing `.po` files

```bash
POT="$module/i18n/${module}.pot"
for po in "$module/i18n"/*.po; do
  [ -f "$po" ] || continue
  base=$(basename "$po" .po)
  [ "$base" = "en" ] && continue
  msgmerge -U --backup=none "$po" "$POT"
done
```

## Add a language

```bash
POT="$module/i18n/${module}.pot"
lang="es_MX"   # example
msginit -i "$POT" -o "$module/i18n/${lang}.po" -l "$lang" --no-translator
# then fill msgstr entries
```

## Validate

```bash
# syntax
for po in "$module/i18n"/*.po; do
  [ -f "$po" ] || continue
  msgfmt -c -o /dev/null "$po" || echo "FAIL $po"
done

# OCA pre-commit (when configured)
pre-commit run oca-checks-po --files "$module"/i18n/* || true
pre-commit run -a   # before push if the repo uses the full gate
```

## Choosing languages (OCA / multi-addon repos)

When preparing i18n for an OCA-style repo without an explicit `$langs` list:

```bash
# Languages already present on this module + a sibling with same prefix
MODULE_LANGS=$(ls "$module/i18n"/*.po 2>/dev/null | xargs -n1 basename | sed 's/.po$//' | grep -vx en)
REF=$(git ls-tree --name-only "origin/${series:-HEAD}" | while read d; do
  [ "$d" = "$module" ] && continue; [ -d "$d/i18n" ] || continue
  case "$d" in ${module%%_*}_*) echo "$d"; break ;; esac
done)
REF_LANGS=$(ls "$REF/i18n"/*.po 2>/dev/null | xargs -n1 basename | sed 's/.po$//' | grep -vx en)
printf '%s\n%s\n' "$MODULE_LANGS" "$REF_LANGS" | sort -u | grep -vx en
```

## Commit

Always `[UPD]` and Assisted-by — [../../shared/git-commit.md](../../shared/git-commit.md):

```bash
git add "$module/i18n/"
git commit -m "$(cat <<'EOF'
[UPD] Update ${module}.pot

Assisted-by: Cursor <cursoragent@cursor.com>
EOF
)"
```

If the change is only one language: `[UPD] ${module}: ${lang} translation`.

## Hand off to Weblate

After a `.pot` reaches the OCA series branch (merged PR / CI), Weblate should create or refresh the component. Further `.po` work for that OCA module moves to [weblate.md](weblate.md).
