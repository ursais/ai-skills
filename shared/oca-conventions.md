# OCA Conventions (shared)

Apply on every new or migrated addon before the validation gate.

## Manifest keys (required)

Every addon `__manifest__.py` **must** include:

| Key | Type | Example | Notes |
|-----|------|---------|-------|
| `development_status` | string | `"Beta"` | One of: `Alpha`, `Beta`, `Production/Stable`, `Mature` |
| `maintainers` | list of GitHub logins | `["$maintainer"]` | OCA key is **`maintainers`** (plural) |

```python
"development_status": "Beta",
"maintainers": ["$maintainer"],
```

`$maintainer` is `maintainer` in [contributor.md](contributor.md). When that field is blank, use `gh api user -q .login`.

- New modules: set both in the scaffold (default `Beta`; maintainer from the profile unless the issue names someone else).
- Migrations: if missing on `$source_ver`, **add** them before `[MIG]` / before opening the PR.
- Prefer matching sibling modules on `origin/$target_ver` for `development_status`.

**PR review:** missing either key is a **must-fix** — request changes and add `needs fixing` ([oca-pr.md](oca-pr.md)).

## Copyright and license

- Manifest: `"license": "AGPL-3"`
- Short 2-line header in every `.py` file (preserve original copyright on migrations):

```python
# Copyright (C) YYYY Author (<url>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
```

New files you add use [contributor.md](contributor.md). `$author_name` and `$author_url` must be filled in. Year is the current calendar year. Do not rewrite copyright on files you did not author.

```python
# Copyright (C) YYYY $author_name (<$author_url>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
```

## Credits

Edit `$module/readme/CONTRIBUTORS.md` (source of truth); regenerate via pre-commit.

When you author or migrate a module, add the profile author if that person is not already listed. Do not replace other authors.

```markdown
- [$author_name]($author_url):
  - $author_name \<<$author_email>\>
```

## Readme fragments

Edit only `readme/*.md` — never hand-edit `README.rst` or `static/description/index.html`.

| File | Content |
|------|---------|
| `DESCRIPTION.md` | What the module adds |
| `CONFIGURE.md` | One-time setup |
| `USAGE.md` | Day-to-day workflow |
| `CONTRIBUTORS.md` | Authors |
| `INSTALL.md` / `CREDITS.md` / `ROADMAP.md` | Only if factual |

Verify menus: `rg -n 'menuitem|act_window' "$module/views" "$module/data"`

```bash
pre-commit run --files "$module/readme/"*.md "$module/README.rst" \
  "$module/static/description/index.html" 2>/dev/null || true
```

## Icon

Copy from a sibling on `origin/$target_ver` (same prefix/family):

```bash
REF=$(git ls-tree --name-only origin/$target_ver | while read d; do
  [ -f "$d/static/description/icon.png" ] || continue
  case "$d" in ${module%%_*}_*) echo "$d"; break ;; esac
done)
[ -n "$REF" ] && cp "$REF/static/description/icon.png" "$module/static/description/icon.png"
```

## Demo data

**One XML file per model** under `demo/`:

```
demo/${module}_${model_suffix}.xml
```

Never mix multiple `model=` values in one demo file. Order `"demo"` in manifest by dependencies.

## i18n

- Separate `[UPD] Update ${module}.pot` commit — never mix into `[MIG]` / `[ADD]` / `[FIX]`
- Never create `en.po`
- Translate languages used by sibling modules on `$target_ver`
- Full workflow (Weblate + local files): **`odoo-translate`** — https://translation.odoo-community.org for OCA `.po`; do not manually push Weblate-managed `.po` to OCA

## Commit tags

| Tag | Use |
|-----|-----|
| `[ADD]` | New module or substantial feature / unit tests |
| `[MIG]` | Migration to a new series |
| `[IMP]` | Improvement |
| `[UPD]` | `.pot` / translations |
| `[FIX]` | Bug or CI fix |
