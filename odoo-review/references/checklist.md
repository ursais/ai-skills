# Odoo module PR review checklist

Use while reviewing the **PR diff** after Gate A (relevance score **≥ 40**). Mark items as must-fix or suggestion.

## Relevance score (Gate A)

See [relevance-score.md](relevance-score.md). Never post “worth reviewing: yes/no”.

- [ ] Score 0–100 from user/OCA value, novelty vs backlog, repo fit (round to multiple of 5)
- [ ] Band: low 0–39 (stop) / medium 40–69 / high 70–100
- [ ] Duplicates / overlap checked; rationale one line
- [ ] If 0–39: soft triage COMMENT only; no human-test assign

## Human-test readiness (Gate C)

- [ ] CI green (ignore codecov/project-only if patch green)
- [ ] No must-fix remaining
- [ ] Human-test path documented: **USAGE/CONFIGURE covers the flow**, or PR has concrete **## Test scenario** (temporary if docs lag)
- [ ] Do **not** require PR Test scenario when USAGE already covers a fix/IMP of an existing flow
- [ ] New/changed user-visible behavior → prefer USAGE update in the PR over a one-off PR scenario
- [ ] Not draft
- [ ] Prefer score ≥ 70 before handing off to `odoo-assign`; if not ready → contributor checklist only

## OCA conventions

See also [../shared/oca-conventions.md](../shared/oca-conventions.md).

- [ ] `__manifest__.py`: `development_status`, `maintainers` (non-empty), `license` AGPL-3
- [ ] Depends list sensible; no unexplained new hard deps
- [ ] Copyright / AGPL headers on new or substantially edited `.py` files
- [ ] CONTRIBUTORS entry for the profile author when they authored or migrated the change
- [ ] Edits only under `readme/*.md` (not hand-edited `README.rst` / `static/description/index.html`)
- [ ] Icon present for new modules; demo files one model per XML
- [ ] No `i18n/en.po`; `.pot` updates not wrongly mixed into unrelated commits when reviewing commit list
- [ ] Access rights / security CSV for new models; record rules if multi-company or restricted docs
- [ ] User-facing behavior reflected in `readme/USAGE.md` (or CONFIGURE) when the PR changes it; PR **## Test scenario** only if docs do not cover the path yet

## Coding standards (Odoo / OCA)

- [ ] Prefer ORM over raw SQL; parameterized SQL only when justified
- [ ] Correct API decorators (`@api.depends`, `@api.onchange`, `@api.constrains`, `model` vs `model_create_multi`)
- [ ] No deprecated APIs for the PR base series (`$target_ver`)
- [ ] XML: correct `inherit_id`, `position`, view priorities; no duplicate xmlids in-module
- [ ] Translations: user-facing strings marked `_()` / `gettext` where required
- [ ] Tests exist or extended for new logic; coverage expectations match [validation-gate](../shared/validation-gate.md) for author workflows
- [ ] pylint-odoo / pre-commit issues visible in CI are addressed or called out

## Architecture / relevance

See [architecture-relevance.md](architecture-relevance.md). Always conclude: fit / questionable / wrong placement.

- [ ] Solution matches the PR/issue goal (no unrelated scope)
- [ ] **New module vs base/existing:** split justified; tiny inherits may belong in the parent module (field-service#1623 pattern)
- [ ] Reuses existing Odoo/OCA patterns instead of parallel custom design where possible
- [ ] Complexity proportional to the problem (no unnecessary models/wizards/bridges)
- [ ] Coupling / upgrade risk called out when overrides are fragile

## Migration script need

See [migration-needed.md](migration-needed.md). Always conclude one of: not required / required+present / required+missing.

- [ ] Diff classified: restart only | `-u` only | needs migration script
- [ ] If schema/data break (rename/remove stored field or model, incompatible type, data move, XML id remap): script present under `$module/migrations/<version>/`
- [ ] If script present: covers every breaking change; idempotent; correct version folder
- [ ] Do **not** demand a script for new fields/models/views/security alone (`-u` is enough)

## Series pitfalls

Checked on 18.0 field-service reviews. A green test can still miss these. Must-fix when the diff does them.

- [ ] `create` overrides on 18.0 are `@api.model_create_multi` and iterate `vals_list`. A single-dict `create` breaks when the caller passes a list.
- [ ] Removed fields are not written. On field-service 18.0, `fsm.order` has `equipment_ids` only; writing `equipment_id` raises `Invalid field`.
- [ ] `account.analytic.line.account_id` is the Projects plan column. An account on another plan is stored with `plan_id._column_name()`. Asserting `account_id` on a non-project plan does not prove the column.
- [ ] An override of `@api.depends` replaces the parent depends. Keep the core dependencies (invoice analytic distribution still depends on product, account, and partner).
- [ ] A stored compute that reads `parent.field` depends on that path (`fsm_parent_id.customer_id`), not only the many2one.
- [ ] A group record rule on a shared model (`account.analytic.line`) with a narrow domain hides every other row from users in that group. Do not add `fsm_order_id != False` as the only rule for FSM groups.
- [ ] A child of a company-scoped model (`fsm.equipment`) has `company_id`, `check_company`, and a company record rule. A SQL model (`_auto = False`) selects `company_id`, groups by it, and has a global company `ir.rule`. Read ACL alone does not apply `fsm.order`'s company rule.
- [ ] `sudo()` covers the reads that raise `AccessError`, not only the `create`. FSM users often cannot read `stock.warehouse`, `stock.picking.type`, or `stock.location`.
- [ ] A button or stat field that reads a model the FSM user cannot read (`purchase.request`) has that model's group. A count with no `groups=` AccessErrors when the order form opens.
- [ ] A smart button that only opens a filtered list does not create the link. The field is on the form, or the action sets the default.
- [ ] Do not group by a properties field as a whole (`group_by: fsm_order_properties`). Odoo raises `ValueError: You must choose the property you want to group by.` Put the field on the search view.
- [ ] An internal picking type is searched in the location's company. Do not validate a serial that was not reserved; `action_assign` can reserve another lot, and overwriting `lot_id` moves the wrong one.
- [ ] `stock.move.fsm_order_id` is not filled by `stock.picking.fsm_order_id` (related to the procurement group). The order Operations list stays empty until the move is linked.
- [ ] A public controller does not `sudo().browse(id)` after `AccessError`. Sequential ids are not secrets; record rules do not apply under `sudo()`. Use an access token.
- [ ] Inherited QWeb that does `t-set="nbCols"` on `hr_timesheet.timesheet_table` fails: the table totals use `colspan="100"` and never define `nbCols`.
- [ ] `pre_init_hook` does not raw-insert with a hardcoded id (`maintenance_team_id = 1`) or skip `company_id`. `ALTER` is idempotent.
- [ ] The PR does not edit a second module's tests to satisfy this module. One module per PR.
- [ ] A hard dependency has an `$target_ver` wheel (`odoo-addon-<name>==18.0.*`). An unreleased addon fails install even when the Python code is fine.
- [ ] User-facing source strings are English. `list` is the 18.0 view mode, not `tree`.

## Bugs / correctness

- [ ] Domains, defaults, and computed fields match stated intent
- [ ] `ensure_one()` / empty-recordset handling where methods assume a single record
- [ ] Onchange vs compute consistency; inverse methods if needed
- [ ] Upgrade / migration scripts (`migrations/`, `pre_init_hook`, `post_init_hook`) safe and idempotent when present
- [ ] No leftover debug (`pdb`, `print`, hardcoded test credentials)
- [ ] Edge cases introduced by the change (empty lines, archived records, multi-company)

## Security

- [ ] New models: `ir.model.access.csv` (+ rules if needed); no accidental public write/create
- [ ] `sudo()` / `with_user` justified and minimal
- [ ] Controllers: auth (`user`/`public`/`none`) appropriate; CSRF for mutating routes
- [ ] No string-built SQL or unsafe `safe_eval` on user input
- [ ] QWeb / reports: escape user content; no arbitrary HTML injection
- [ ] Sensitive fields (`groups=`, password-like) protected
- [ ] Attachment / filestore paths not user-controlled without checks

## Performance

Deep-review companion: run the parallel agent in [performance-review.md](performance-review.md). Still verify these against the diff:

- [ ] No obvious N+1 (`search`/`browse` inside loops over large sets) without prefetch/`mapped`
- [ ] Hot-path searches use domains/indexes thoughtfully; unbounded searches called out
- [ ] Stored computes / related fields used where repeated reads matter
- [ ] Avoid unnecessary `invalidate_recordset` / `flush` in loops
- [ ] Heavy work not done in `onchange` when it belongs in create/write or cron
- [ ] Batch `create`/`write` where the diff introduces multi-record flows

## CI mapping (failures → ask author)

| Check family | Typical ask |
|--------------|-------------|
| pre-commit / prettier / eslint | Fix formatting/hooks in module |
| pylint / flake8 | Fix reported findings |
| tests | Fix code or add/adjust tests |
| codecov/patch | Cover new lines |
| codecov/project only | Out of scope if patch green |
| runboat / install | Fix install/manifest/data load |
| dependency / unreleased | Fix `depends` or wait on dep PR |
