---
name: odoo-translate
description: >
  Translate OCA modules via Weblate (translation.odoo-community.org) and otherwise manage
  module i18n/ (.pot / .po): export templates, msgmerge, new languages, [UPD] commits.
  Use when translating an OCA addon, fixing i18n, updating .pot, adding a language, or
  /odoo-translate. Not for module code (odoo-dev), migrations (odoo-migrate), bug fixes
  (odoo-fix), or PR review (odoo-review).
---

# Odoo / OCA Translate

Translate `$module` (and keep `i18n/` healthy). **Prefer OCA Weblate** when the addon is on OCA; otherwise manage files under `$module/i18n/` locally.

**Platform (shared):** [oca-conventions](../shared/oca-conventions.md) · [git-commit](../shared/git-commit.md) · [git-one-module](../shared/git-one-module.md) · [ursais-remote](../shared/ursais-remote.md) · [oca-pr](../shared/oca-pr.md)

## Invocation

```
/odoo-translate
/odoo-translate OCA/field-service fieldservice es_MX
/odoo-translate $module --langs fr,es --series 18.0
```

## Workflow

```
Step 0  Inputs ($module, $langs, $series / $repo, path, WEBLATE_TOKEN)
Step 1  Choose path: Weblate API / Weblate UI vs local i18n/
Step 2a Weblate — API (preferred) or UI / file upload → bot push
Step 2b Local — .pot + .po (makepot / msgmerge / msginit)
Step 3  Commit policy ([UPD] only for local i18n) + report
```

## Core rules

1. **Weblate first for OCA** — https://translation.odoo-community.org is the source of truth for `.po` on OCA main branches ([references/weblate.md](references/weblate.md))  
2. **API when possible** — if `$WEBLATE_TOKEN` (or `$WEBLATE_API_KEY`) is set, use the REST API ([references/weblate-api.md](references/weblate-api.md)); never paste the token into chat  
3. **Never push `.po` manually to OCA** when the component exists on Weblate — use API, UI, or Weblate **file upload**; avoid merge conflicts with the translation bot  
4. **Never create `en.po`** ([oca-conventions](../shared/oca-conventions.md))  
5. **`.pot` updates** are a separate `[UPD] Update ${module}.pot` commit — never mix into `[MIG]` / `[ADD]` / `[FIX]`  
6. **Commits:** `Assisted-by: Cursor`, never `Co-authored-by: Cursor` ([git-commit](../shared/git-commit.md))  
7. One module at a time when opening PRs ([git-one-module](../shared/git-one-module.md))  

## Step 0 — Inputs

| Variable | Example | Notes |
|----------|---------|-------|
| `$module` | `fieldservice` | Addon technical name |
| `$repo` | `field-service` | OCA repo (Weblate project stem) |
| `$series` | `18.0` | Branch / Weblate project suffix |
| `$langs` | `es_MX`, `fr` | Target language codes (ask if missing) |
| `$ROOT` | path to checkout | Local module tree when not using Weblate only |
| `$WEBLATE_TOKEN` | `wlu_…` | From Weblate profile → API; export in shell, do not paste in chat |

Ask for `$module` and `$langs` if missing. Derive `$repo` / `$series` from the checkout or PR when possible.

## Step 1 — Choose path

| Situation | Path |
|-----------|------|
| OCA module on a supported series, component visible on Weblate | **Weblate** (Step 2a) |
| OCA module not yet on Weblate (no `.pot` on branch / component missing) | Ensure `.pot` lands on the series branch (CI `MAKEPOT` / local export + merge), then Weblate discovers it; until then use **local** for templates only |
| Private / customer / non-OCA addon | **Local i18n/** (Step 2b) |
| Offline bulk translate for an OCA component | Translate elsewhere → **Weblate upload** (still not a manual `.po` push to GitHub) |

Weblate layout: **project** `{repo}-{series}` (e.g. `field-service-18.0`), **component** `{repo}-{series}-{module}`. URL pattern:

```text
https://translation.odoo-community.org/projects/{repo}-{series}/{repo}-{series}-{module}/
```

## Step 2a — Weblate (OCA)

Follow [references/weblate.md](references/weblate.md) and [references/weblate-api.md](references/weblate-api.md).

1. Register at https://translation.odoo-community.org with **GitHub** login  
2. Email **transbot@odoo-community.org** with GitHub username + language(s) if not yet granted  
3. **API (preferred):** user creates a token in Weblate profile → `export WEBLATE_TOKEN=…` in the shell  
   - Resolve project/component slugs via `/api/projects/` and `/api/components/`  
   - List empty units, `PATCH /api/units/{id}/`, or `POST …/translations/…/file/` with a `.po`  
4. **UI fallback:** translate in the browser or upload a `.po` if no token / no write scope  
5. Do **not** open a GitHub PR that only edits Weblate-managed `.po` files  
6. Weblate commits/pushes to GitHub on its schedule (historically ~24h; do not force-push over bot commits)  
7. Report: Weblate URL, languages, % done / remaining strings, API vs upload  

Translator docs: https://docs.weblate.org/en/latest/user/translating.html  
OCA entry: https://www.odoo-community.org/resources/translate  

## Step 2b — Local i18n/ (otherwise)

Follow [references/i18n-files.md](references/i18n-files.md).

1. Export / refresh `$module/i18n/${module}.pot` (`click-odoo-makepot` preferred)  
2. For each `$lang` in `$langs`: `msgmerge` existing `.po`, or `msginit` for new languages  
3. Fill translations (agent or human); keep gettext headers sane; run `msgfmt -c` / pre-commit `oca-checks-po` when available  
4. Never add `i18n/en.po`  
5. Match sibling-module languages on the same series when choosing defaults for OCA work  

```bash
POT="$module/i18n/${module}.pot"
# makepot → then per lang:
msgmerge -U "$module/i18n/${lang}.po" "$POT"
# or: msginit -i "$POT" -o "$module/i18n/${lang}.po" -l "$lang" --no-translator
```

## Step 3 — Commit + report

When local files change (non-Weblate or `.pot` only on a ursais PR):

```bash
git add "$module/i18n/"
git commit -m "$(cat <<'EOF'
[UPD] Update ${module}.pot

Assisted-by: Cursor <cursoragent@cursor.com>
EOF
)"
```

Use a clearer subject if the commit is language-only, e.g. `[UPD] ${module}: ${lang} translation`, still tag `[UPD]`.

Push/PR via [ursais-remote](../shared/ursais-remote.md) + [oca-pr](../shared/oca-pr.md) only when the change belongs in a module PR (template update, private repo, or series not on Weblate).

### Report

```
Translate complete
- Module: $module
- Series / repo: $series / OCA/$repo (if any)
- Path: Weblate | local i18n/
- Weblate: <url> | n/a
- Languages: …
- .pot refreshed: yes | no
- Commit / PR: <sha or url> | none (Weblate-only)
- Next: wait for Weblate bot | review .po | add language on Weblate
```

## Not this skill

| Need | Skill |
|------|--------|
| New module / feature code | `odoo-dev` |
| Series port | `odoo-migrate` |
| Functional bug fix | `odoo-fix` |
| Review someone else's PR | `odoo-review` |

## Skill-specific references

| File | Contents |
|------|----------|
| [references/weblate.md](references/weblate.md) | OCA Weblate account, project URLs, do/don't |
| [references/weblate-api.md](references/weblate-api.md) | `WEBLATE_TOKEN`, REST calls, upload, unit PATCH |
| [references/i18n-files.md](references/i18n-files.md) | Local `.pot` / `.po` commands and checks |
