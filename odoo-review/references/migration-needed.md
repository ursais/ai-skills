# When does the PR need a migration script?

Inspect the **diff** (models, fields, XML ids, data). Classify operator impact the same way as [odoo-merge semver](../../odoo-merge/references/semver-bump.md):

| Class | Operator action | Migration script? |
|-------|-----------------|-------------------|
| **patch** | Server restart enough | No |
| **minor** | Module upgrade (`-u`) enough | No — ORM/load handles new fields/models/XML |
| **major** | Custom data/schema move | **Yes — must be in this PR** |

## Migration script **required** (must-fix if missing)

Flag **must-fix** when the diff does any of the following **and** the PR has no script under e.g. `$module/migrations/<version>/` (`pre-migrate.py`, `post-migrate.py`, `end-migrate.py`) or an equivalent documented hook that performs the same work:

- **Rename or remove** a stored field that may already hold data in production
- **Incompatible field type / relation change** (e.g. `Char`→`Many2one`, `Many2one`→`Many2many`, changing `comodel_name` on a stored relation)
- **Rename or remove** a model (`_name`) that may already have rows / `ir.model.data`
- **Move data** between models/tables or split/merge records
- **Rename / remove XML ids** (`ir.model.data`) that other modules or DB rows reference and that need remapping
- **Change selection keys** or stored compute results that leave invalid values in DB without a cleanup
- **Remove columns/tables** or otherwise drop DB structures that still contain data to preserve
- Any change the author describes as needing a script, or that cannot be applied safely with `-u` alone

Also must-fix when a migration script **is present** but incomplete: not idempotent, wrong version folder, missing `pre`/`post` for the stated change, or does not cover all renamed/removed fields in the diff.

## Migration script **not** required (upgrade / restart only)

Do **not** demand a migration script for:

- New models / new nullable fields / new non-stored fields
- New views, actions, menus, security CSV rows, reports (standard `-u` load)
- Pure Python/JS logic fixes with no schema or stored-data change
- i18n, tests, CI, readme, icons
- Adding an index / `sql_constraints` that do not rewrite existing values (still note if a heavy lock is a concern — suggestion, not migration-script must-fix)

These are **minor** (needs `-u`) or **patch** (restart only) for merge bump purposes — mention the class in Notes, but do not request a migration script.

## How to check the PR

```bash
# Files touching schema / data
gh pr diff "$PR_NUMBER" --repo "$OWNER/$repo" --name-only | rg 'models/|__manifest__\.py|migrations/|security/|data/|\.xml$'

# Migration scripts added in the PR
gh pr diff "$PR_NUMBER" --repo "$OWNER/$repo" --name-only | rg '/migrations/.*/(pre|post|end)-migrate\.py$' || true
```

In the review body, always state one of:

- **Migration script:** not required (restart / `-u` only) — brief why
- **Migration script:** required and present — list path(s)
- **Migration script:** required but missing — must-fix checkbox listing the schema/data changes that need it
