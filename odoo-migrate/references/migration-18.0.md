# Before migrating

* Update yourself with the latest OCA Conventions: https://odoo-community.org/page/contributing
* Subscribe to the mailing list of the related project: https://odoo-community.org/groups
* On the corresponding GitHub issue named "Migration to version 18.0", announce which module(s) you want to migrate
* [[Install pre-commit]]

# Tasks to do in the migration

**REMARK:** Here, we are highlighting **framework changes** from previous version to this one, not data-model changes, as they are very extensive, and the alternative may depends on the module requirements, nor business methods changes. You can check data-model changes for each core module in the `upgrade_analysis.txt` files inside OpenUpgrade project: https://github.com/OCA/OpenUpgrade.

**REMARK 2**: If you are doing a migration jumping several versions, please check all the tasks in the successive "Migration to version XX.0" guides until arriving to this one.

* Bump module version to `18.0.1.0.0`.
* Remove any possible migration script from previous version (in a nutshell, remove `migrations` folder inside the module if exists).
* Remove references in CREDITS.rst of past financed migrations by other companies.
* If you are comfortable with squashing commits in Git, you could consider to squash administrative commits (if any) with the previous commit for reducing commit noise. Check https://github.com/OCA/maintainer-tools/wiki/Merge-commits-in-pull-requests#mergesquash-the-commits-generated-by-bots-or-weblate for details.
* Replace `tree` view type by `list`. This means everywhere in Python, JS or XML where there's a mentioning of this type, but keep XML-IDs that contain `tree` in its name for avoiding subsequent changes in dependent modules.

  There's a script that automates most of the work provided by Odoo itself. To use it, have a local minimal Odoo installation, and run:

  ```shell
  <path_to_odoo>/odoo-bin --addons-path=${YOUR_PROJECT} upgrade_code --script 17.5-01-tree-to-list.py
  ```

  See this global change with examples in the Odoo PR: https://github.com/odoo/odoo/pull/159909.

  Note that there's a context key for selecting specific list view ref, that must be changed from `tree_view_ref` to `list_view_ref`.
* `user_has_groups` has been removed, so now you should use `self.env.user.has_group`. More details and examples of the replacement in https://github.com/odoo/odoo/pull/151597.
* Methods `check_access_rights()` and `check_access_rule()` are replaced by a single method `check_access()`, the same as `_filter_access_rules()` and `_filter_access_rules_python()` by `_filtered_access()`. More info at https://github.com/odoo/odoo/pull/179148.
* `_name_search` is gone, replaced by `_search_display_name`.
* Replace the deprecated `_check_recursion()` method by `_has_cycle()`.
* `copy` and `copy_data` now work on multiple records. This means that `copy_data` returns a list of values, and `self` may be a multi-recordset. Reference: https://github.com/odoo/odoo/pull/154132
* On fields definitions, replace the obsolete attribute `group_operator` by `aggregator`. Reference: https://github.com/odoo/odoo/commit/dd7a10aa07d1110608273a3002a985a6df6255bc and https://github.com/odoo/odoo/pull/127353/commits/e0280ed070c7927b8b8e8933ba381199a6a1ed4c
* Be careful with searches on non stored related fields: they don't log a warning anymore, they throw an exception.
* If overriding `search` method for modifying searches result, take into account that this method is not always called in this version. Override `search_fetch` instead.
* Whenever possible, define the field `path` on `ir.actions.act_window` records for a nicer URL.
* The `<div class="oe_chatter">` with all its inner stuff now converts into just `<chatter />`. See https://github.com/odoo/odoo/pull/156463 for more details and sample replacements.
* Missing fields used in expressions (invisible, column_invisible, readonly, required, context, domain) are now added to the views as invisible ones automatically. If you encounter fields in views with `invisible="True"` or `invisible="1"`, they can probably be removed for cleanliness, as they are auto-added. Reference: https://github.com/odoo/odoo/pull/137031.
* The kanban views arch have been simplified:
  * `kanban-box` is replaced by `card` definition.
  * The elements are now put as regular `<field>` definitions with no embracing `<div>`. Additional `class` attributes may condition the place where they are put.
  * `kanban-tooltip` has been removed.
  * Weird syntax like `<ul class="oe_kanban_colorpicker" data-field="color"/>` can now be expressed as `<field name="color" widget="kanban_color_picker"/>`.
  * For showing an image for a many2one field, do `<field name="parent_id" widget="image" options="{'preview_image': 'document'}"/>`.

  More info at [odoo/odoo#167751](https://github.com/odoo/odoo/pull/167751).
* `/** @odoo-module **/` can be removed from the JS files. Reference: https://github.com/odoo/odoo/pull/142858
* Instead of doing `from odoo import registry` and then `registry(db_name)`, now you have to do `from odoo.modules.registry import Registry` and `Registry(db_name)`. More info at https://github.com/odoo/odoo/pull/178784.
* You can replace the call to translate a string (`_`) with `self.env._` for getting some performance improvement in some cases. See https://github.com/odoo/odoo/pull/174844.
* If the module contains any company dependent field, a migration script is required for the OpenUpgrade path. Example: https://github.com/OCA/sale-workflow/pull/3958/files.
* On JS test tours, `extra_trigger` is not used anymore. Instead, you need to add an extra independent step with this `extra_trigger` as the `trigger`. Example: https://github.com/OCA/e-commerce/pull/1011/commits/c53530c322bb478d329601d3910e3be974223432#diff-0c223ef2d79e98fced67d796049ac325cce1155ab70266f5c22d12ed0944c495L20-L22
* Add tests to increase code coverage.
* Disable tracking by setting `tracking_disable` on the whole test env (eg: `cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))` ) or evaluate the use of `BaseCommon` as base test class if you need to setup company, currency, users and groups in a special way)
* Check tasks of previous versions if you are migrating from lower versions than 17. It's also recommended to check past migration guides for things not done in previous migrations.
* Do the rest of the changes you need to perform for making the module works on the new version.

# Tasks NOT to do in the migration

* change copyright year

  A line like this:

  ```
  # Copyright 2024 ACME Ltd - Johnny Glamour
  ```
  says "copyright FROM 2024". There's no need to change the year to the current one.

* change original authors

# How-to

## Technical method to migrate a module from "17.0" to "18.0" branch

* `$repo`: the OCA repository hosting the module
* `$module`: the name of the module you want to migrate
* `$user_org`: `$fork_owner` from [contributor.md](../../shared/contributor.md)

**Full process**

* On a shell command:
  ```bash
  $ git clone https://github.com/OCA/$repo -b 18.0
  $ cd $repo
  $ git checkout -b 18.0-mig-$module origin/18.0
  $ git format-patch --keep-subject --stdout origin/18.0..origin/17.0 -- $module | git am -3 --keep
  $ pre-commit run -a  # to run pre-commit linters and formatters (please ignore pylint errors at this stage)
  $ git add -A
  $ git commit --no-verify -m "$(cat <<'EOF'
[IMP] $module: pre-commit auto fixes

Assisted-by: Cursor <cursoragent@cursor.com>
EOF
)"  # it is important to do all the formatting in one commit the first time; never Co-authored-by Cursor
  ```
* On the last step, there may be no changes done by pre-commit, so just ignore the message saying "Nothing to commit".
* Check https://github.com/OCA/maintainer-tools/wiki/Merge-commits-in-pull-requests for a procedure for reducing commits from "OCA Transbot...".
* If the **module is renamed** in the migration, you have to rename the whole commit history. If not done, on the next version, when these commands will be executed again, only the latest commit will be brought. For doing the renaming, execute the following commands:
  ```
  git filter-branch --tree-filter 'if [ -d $module ]; then mv $module $new_module_name; fi' HEAD
  git rebase origin/18.0
  ```
* Adapt the module to the 18.0 version following [tasks to do](https://github.com/OCA/maintainer-tools/wiki/Migration-to-version-18.0#tasks-to-do-in-the-migration).
* On a shell command, type this for uploading the content to GitHub:
  ```bash
  $ git add --all
  $ git commit -m "$(cat <<'EOF'
[MIG] $module: Migration to 18.0

Assisted-by: Cursor <cursoragent@cursor.com>
EOF
)"
  $ git remote add $user_org git@github.com:$user_org/$repo.git # This mode requires an SSH key in the GitHub account
  $ ... or ....
  $ git remote add $user_org https://github.com/$user_org/$repo.git # This will required to enter user/password each time
  $ git push $user_org 18.0-mig-$module --set-upstream
  ```
* Follow the link on the command line or check in https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request-from-a-fork how to create the pull request.
* For being easily searchable and avoiding to duplicate efforts, please name the pull request following this pattern: `[18.0][MIG] <module>: Migration to 18.0`.

**Troubleshooting**

Sometimes, when performing these operations, the process can hang due to conflicts on the patches being applied. One of the possible problems is because a patch removes entirely a file and `git am` is not able to resolve this. It ends with a message `error: ...: patch does not apply`.

If that's your case, you can add `--ignore-whitespace` at the end of the `git am` command for allowing the patch to be applied, although there will be still conflicts to be solved, but they will be doable through standard conflict resolution system. Starting from the previous situation, you will need to do:

```bash
git am --abort
git format-patch --keep-subject --stdout origin/18.0..origin/17.0 -- <module path> | git am -3 --keep --ignore-whitespace
# resolve conflicts (for example git rm <file>)
git add --all
git am --continue
```
