# Migration to version 19.0

Source of truth:
[OCA maintainer-tools — Migration to version 19.0](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-19.0)

OpenUpgrade: https://github.com/OCA/OpenUpgrade

**If migrating onward to 20.0**, continue with [migration-20.0.md](migration-20.0.md) after this guide.

## Before migrating

* OCA Conventions: https://odoo-community.org/page/contributing
* Project mailing list: https://odoo-community.org/groups
* Announce on the GitHub issue "Migration to version 19.0"
* Install pre-commit

## Tasks to do in the migration

**REMARK:** Framework changes only — not full data-model / business APIs. Use OpenUpgrade `upgrade_analysis.txt` for model diffs.

**REMARK 2:** Jumping several versions → apply all intermediate migration guides first.

* Bump module version to `19.0.1.0.0`.
* Remove previous-version `migrations/` folder if present.
* Remove past financed-migration credits in CREDITS.rst.
* Optional: squash administrative commits (Transbot/Weblate) — https://github.com/OCA/maintainer-tools/wiki/Merge-commits-in-pull-requests#mergesquash-the-commits-generated-by-bots-or-weblate
* On `res.groups`, `category_id` → `privilege_id` (`res.groups.privilege`). https://github.com/odoo/odoo/commit/33637d137ed52f5faabaafd5c208e187042be8eb
* Replace `groups_id` by `group_ids` on views, menus, actions, reports, `res.users`, `website.page.properties`, etc. https://github.com/odoo/odoo/pull/179354
* Replace `self._cr` → `self.env.cr`, `self._uid` → `self.env.uid`, `self._context` → `self.env.context`.
* Replace `odoo.osv.expression` by `odoo.fields.Domain`. https://github.com/odoo/odoo/pull/217708
* Replace `_sql_constraints` by `models.Constraint` / `models.Index`. https://github.com/odoo/odoo/pull/175783
* Prefer `self.env.tz` over manual pytz / context `tz` handling. https://github.com/odoo/odoo/pull/221541
* Field attribute `auto_join` → `bypass_search_access`. https://github.com/odoo/odoo/pull/219627
* Replace `read_group` by `_read_group` (backend) or `formatted_read_group` (public). https://github.com/odoo/odoo/pull/163300
* Controllers: `@route` `type="json"` → `type="jsonrpc"`. https://github.com/odoo/odoo/pull/183636
* Search methods of non-stored computed fields return a `Domain` object (not a list). Domain optimizer may change operator/value (e.g. `=` True → `in` OrderedSet).
* Prefer `Domain` objects in searches / `filtered_domain`. Example: https://github.com/OCA/commission/pull/646
* `toggle_active` → explicit `action_archive` / `action_unarchive`. https://github.com/odoo/odoo/pull/183691
* Consider `@api.private` on public-named methods that must not be RPC-accessible. https://github.com/odoo/odoo/pull/195402
* Dynamic date domain parameters: https://github.com/odoo/odoo/pull/216665
* Import `SUPERUSER_ID` from `odoo.api`, not `odoo`.
* `@ormcache_context` → `@ormcache` with `self.env.context.get("key")`. https://github.com/odoo/odoo/pull/220725
* Prefer `odoo.tools.urls.urljoin` over `urllib.parse.urljoin`.
* `name_search`: parameter `args` → `domain`.
* Remove `@api.returns` and adapt callers. https://github.com/odoo/odoo/pull/182709
* Decimal precision name `Product Unit of Measure` → `Product Unit` (silent fallback to 2 decimals if unchanged).
* Remove `string` / `expand` from `<group>` tags in search views. https://github.com/odoo/odoo/pull/220023
* Add tests; coverage **> 99%** before `[MIG]` (skill gate).
* Disable tracking in tests or use `BaseCommon` appropriately.
* Demo data is **not** installed by default — create test data in the tests themselves.
* Fake models in tests: prefer native registry helpers over `odoo-test-helper` (`add_to_registry` pattern from the wiki).
* Check earlier migration guides if source &lt; 18.0.
* Remaining changes needed for 19.0.

## Tasks NOT to do

* Do not change copyright years (“Copyright 2024 …” means from 2024).
* Do not change original authors.

## How-to (18.0 → 19.0)

```bash
git clone https://github.com/OCA/$repo -b 19.0
cd $repo
git checkout -b 19.0-mig-$module origin/19.0
git format-patch --keep-subject --stdout origin/19.0..origin/18.0 -- $module | git am -3 --keep
pre-commit run -a
git add -A
git commit --no-verify -m "$(cat <<'EOF'
[IMP] $module: pre-commit auto fixes

Assisted-by: Cursor <cursoragent@cursor.com>
EOF
)"
# adapt module to 19.0 (tasks above)
git add --all
git commit -m "$(cat <<'EOF'
[MIG] $module: Migration to 19.0

Assisted-by: Cursor <cursoragent@cursor.com>
EOF
)"
git push ursais 19.0-mig-$module --set-upstream
```

PR title: `[19.0][MIG] <module>: Migration to 19.0`.

On `git am` failures for removed files, retry with `--ignore-whitespace` (same pattern as other migration guides).
