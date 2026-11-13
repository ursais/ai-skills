# Migration to version 20.0

Source of truth (keep in sync when the wiki changes):
[OCA maintainer-tools — Migration to version 20.0](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-20.0)

OpenUpgrade data-model diffs: https://github.com/OCA/OpenUpgrade (`upgrade_analysis.txt` per core module).

**If migrating from lower than 19.0**, also apply successive guides ([migration-19.0.md](migration-19.0.md), [migration-18.0.md](migration-18.0.md), …) before / with this one.

## Before migrating

* Update yourself with the latest OCA Conventions: https://odoo-community.org/page/contributing
* Subscribe to the mailing list of the related project: https://odoo-community.org/groups
* On the corresponding GitHub issue named "Migration to version 20.0", announce which module(s) you want to migrate
* [[Install pre-commit]]

## Tasks to do in the migration

**REMARK:** Framework changes from the previous version, not full data-model or business-method changes. Check OpenUpgrade analyses for model field renames/removals.

**REMARK 2:** Jumping several versions → follow all intermediate "Migration to version XX.0" guides until this one.

* Bump module version to `20.0.1.0.0`.
* Remove any possible migration script from previous version (remove `migrations/` inside the module if it exists).
* Remove references in CREDITS.rst of past financed migrations by other companies.
* If comfortable squashing commits, squash administrative commits with the previous commit to reduce noise. See https://github.com/OCA/maintainer-tools/wiki/Merge-commits-in-pull-requests#mergesquash-the-commits-generated-by-bots-or-weblate.
* **Access rights + record rules → `ir.access`:** merge `ir.model.access.csv` and `ir.rule` XML into model `ir.access`, usually loaded as `security/ir.access.csv`. Details/examples: https://github.com/odoo/odoo/pull/166359.

  Prefer Odoo’s mostly automatic rewrite (from an Odoo 20 tree):

  ```shell
  <path_to_odoo>/odoo-bin --addons-path=${YOUR_PROJECT} upgrade_code --script 19.4-00-ir-access.py
  ```

  Then:
  * Review logs (`INFO` / `WARNING` / `ERROR`) — treat a clean run as a **starting point**, not finished.
  * Watch **group inheritance** warnings: a row without `group_id` can become a **global** permission/restriction.
  * Update `__manifest__.py` `data` to load `security/ir.access.csv` instead of `ir.model.access.csv` / rule XML.
  * Typical CSV header: `id,name,model_id,group_id/id,operation,domain` (`operation` is a subset of `crud`, e.g. `r`, `ru`, `cru`, `crud`).

  List available scripts with `ls <path_to_odoo>/odoo/upgrade_code/` if names differ in your Odoo build.

* **Font Awesome → Material Symbols / Odoo UI icons:** convert UI icons declared with `class="fa-…"` (and legacy `oi oi-…`) to the new system. Guide: https://www.odoo.com/documentation/20.0/developer/reference/user_interface/icons.html

  Prefer Odoo’s `upgrade_code` icon script when present (best-effort; review runtime-built class names manually):

  ```shell
  <path_to_odoo>/odoo-bin --addons-path=${YOUR_PROJECT} upgrade_code --from 19.0 --to 20.0 --glob '${module}/**/*'
  # or run the specific icon script name listed under odoo/upgrade_code/
  ```

  Manual shape:

  ```xml
  <!-- old -->
  <i class="fa fa-user"/>
  <!-- new -->
  <i class="oi oi-filled" data-icon="person"/>
  ```

  Map modifiers (`fa-lg` → `oi-lg`, `fa-2x` → `oi-2x`, `fa-fw` → `oi-fw`, `fa-spin` → `oi-spin`, `fa-pulse` → `oi-pulse`). Brand / Odoo-only glyphs: `data-icon="oi_…"`.

* If tests use `BaseCommon`, you may need `_test_user_groups = None` on the test class so tests still run as superadmin (uid=1). Without it, tests run as a plain internal user with no extra groups. Alternative: set `_test_user_groups` to an explicit list of group xmlids (can have side effects depending on loaded modules).
* Widget `selection_badge` is split by field type: `badges_selection` for `selection`, `badges_many2one` for `many2one`.
* Add tests to increase code coverage (**> 99%** before `[MIG]` — skill gate).
* Disable tracking in tests (`tracking_disable` on the env) or use `BaseCommon` when appropriate.
* Check tasks of previous versions if migrating from lower than 19.0.
* Do the rest of the changes needed for the module on 20.0.

## Tasks NOT to do in the migration

* change copyright year

  A line like `# Copyright 2024 ACME Ltd - Johnny Glamour` means “copyright **from** 2024”. Do not bump the year.

* change original authors

## How-to

### Technical method to migrate a module from "19.0" to "20.0" branch

* `$repo`: the OCA repository hosting the module
* `$module`: the name of the module you want to migrate
* `$user_org`: your GitHub login or organization name (for this skill: `ursais`)

**Full process**

* On a shell command:

  ```bash
  $ git clone https://github.com/OCA/$repo -b 20.0
  $ cd $repo
  $ git checkout -b 20.0-mig-$module origin/20.0
  $ git format-patch --keep-subject --stdout origin/20.0..origin/19.0 -- $module | git am -3 --keep
  $ pre-commit run -a  # ignore pylint errors at this stage
  $ git add -A
  $ git commit --no-verify -m "$(cat <<'EOF'
  [IMP] $module: pre-commit auto fixes

  Assisted-by: Cursor <cursoragent@cursor.com>
  EOF
  )"  # all formatting in one commit the first time; never Co-authored-by Cursor
  ```

* If pre-commit made no changes, ignore “Nothing to commit”.
* Reduce Transbot / Weblate noise: https://github.com/OCA/maintainer-tools/wiki/Merge-commits-in-pull-requests
* If the **module is renamed**, rewrite history so future `format-patch` still brings the full chain:

  ```bash
  # older git
  git filter-branch --tree-filter 'if [ -d $module ]; then mv $module $new_module_name; fi' HEAD
  git rebase origin/20.0

  # newer git (preferred when available)
  git filter-repo --path-rename $module/:$new_module_name/ --refs HEAD --force
  ```

* Adapt the module to 20.0 following [tasks to do](#tasks-to-do-in-the-migration) and the wiki.
* Upload:

  ```bash
  $ git add --all
  $ git commit -m "$(cat <<'EOF'
  [MIG] $module: Migration to 20.0

  Assisted-by: Cursor <cursoragent@cursor.com>
  EOF
  )"
  $ git remote add $user_org git@github.com:$user_org/$repo.git
  $ git push $user_org 20.0-mig-$module --set-upstream
  ```

* Open the PR. Title pattern: `[20.0][MIG] <module>: Migration to 20.0`.

**Troubleshooting**

If `git am` fails with `patch does not apply` (often full file removal):

```bash
git am --abort
git format-patch --keep-subject --stdout origin/20.0..origin/19.0 -- $module | git am -3 --keep --ignore-whitespace
# resolve conflicts (e.g. git rm <file>)
git add --all
git am --continue
```

## Skill workflow note

This repo’s `/odoo-migrate` skill still owns: one module per branch, validation gate (>99% coverage), separate `[UPD]` pot, push to **ursais**, PR labels/milestone, `/ocabot migration $module`. Use this guide for **framework** tasks inside Step 3.
