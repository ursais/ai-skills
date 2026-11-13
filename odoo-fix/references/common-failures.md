# Common Odoo Module Failures

Symptom-first catalog. Always confirm against the actual traceback — these are starting points, not guesses.

---

## Manifest and dependencies

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError: No module named 'odoo.addons.foo'` | Missing `depends` or addon not on path | Add to `depends`; verify addons-path includes repo |
| Install order error / circular dependency | Bad `depends` chain | Reorder or split module; remove false dependency |
| CI "unreleased dependencies" | Depends on module not in target branch | Fix `depends` or add exclusion; use released version |
| Assets not loading | Missing `assets` key in manifest (16+) | Register JS/SCSS/XML in `__manifest__.py` `assets` |

---

## XML and views

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `ParseError` at line N | Malformed XML, unclosed tag | Fix XML structure |
| `Element '<field name="x">' cannot be located` | Bad xpath / parent view changed | Fix xpath; verify `inherit_id` on correct `$version` |
| `Field "x" does not exist in model "y"` | Typo or field on wrong model | Add field on model or fix view `name` |
| `Label tag must contain a "for"` | Invalid label in form view | Use `for="field_name"` or replace with `<div>` |
| Menu missing but action works | `groups` on menuitem, missing ACL | Check security groups and `ir.model.access.csv` |
| Duplicate field in view | Double xpath insert | Remove duplicate or use `position="replace"` |

**View inheritance debug**

```bash
rg -n "inherit_id|xpath" "$module/views"
rg -n "^\s+$field\s*=" "$module/models"
```

---

## Python / ORM

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `AttributeError: 'super' object has no attribute 'create'` | Wrong `super()` in multi-inherit | Use `super(Model, self).create(vals_list)` pattern for version |
| `TypeError: create() takes 2 positional arguments` | Odoo 17+ `create` expects list | `create([vals])` or accept `vals_list` in override |
| `ValueError: Invalid field 'states' on model` | Removed `states=` on fields (17+) | Use `readonly`/`invisible` attrs in view instead |
| Constraint fires on module install | `@api.constrains` on required related | Defer constraint; use `create`/`write` guards or demo-safe values |
| Computed field not updating | Missing `@api.depends` | Add correct dependency paths |
| `UserError` on save for `_inherits` partner | `partner_id` exposed in form | Keep `partner_id` invisible; set partner fields via related model |
| Double record on create | Missing context flag in `create`/`write` | Use context keys (e.g. `creating_fsm_location`) to skip re-entry |

**Version API reminders**

| Area | 16.0 | 17.0+ |
|------|------|-------|
| `create` override | `def create(self, vals)` | `def create(self, vals_list)` |
| Field `states` | Allowed | Removed — use view attrs |
| `name_get` | Common | Prefer `display_name` / `_compute_display_name` |
| OWL templates | Mixed legacy | Prefer OWL 2 components in assets |

---

## Security

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `AccessError` for normal user | Missing ACL row | Add `ir.model.access.csv` line |
| Sees records from other companies | Missing record rule | Add `ir.rule` with company domain |
| Field visible but not editable | `groups` on field in view | Adjust groups or grant access |
| Portal user blocked | Missing portal ACL / rule | Add portal group access and record rules |

---

## Data and migrations

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Fails only on `-u` | Migration script error | Fix `migrations/$version/pre-*.py` or `post-*.py` |
| Duplicate XML IDs on upgrade | `noupdate="0"` reloading data | Set `noupdate="1"` on stable data or use migration to update |
| Missing default on upgrade | New required field without default | Migration: `openupgrade` pattern or `pre_init_hook` default |
| Works on fresh DB, not production | Stale view/customization in DB | Test with `-u`; compare `ir_ui_view` arch in DB vs file |

---

## JavaScript / OWL / tours

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Blank widget / console `OWL` error | Asset not in manifest bundle | Register in `assets` under correct bundle key |
| Tour fails | Selector changed in core | Update tour selectors; run with `--test-tags /$module` |
| RPC 404 on custom route | Controller not imported | Add controller to `controllers/__init__.py` |

---

## Tests

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `AssertionError` in test | Business logic regression | Fix code; keep test unless requirement changed |
| `TransactionRollbackError` in test | Missing `self.env` flush or bad test isolation | Use `TransactionCase`; call `flush()` where needed |
| Test passes locally, fails CI | Different Odoo version or missing dependency | Match CI command exactly ([testing.md](testing.md)) |
| `SkipTest` / no tests collected | Wrong `--test-tags` | Use `/module_name` or class.method from failure log |

---

## pre-commit / lint (OCA repos)

| Hook / check | Fix |
|--------------|-----|
| `prettier` | Run `pre-commit run prettier --all-files` or apply CI diff |
| `eslint` | Fix `static/src`; run hook locally |
| `pylint_odoo` | Fix reported Python; avoid noqa unless justified |
| `oca-gen-addon-readme` | Edit `readme/*.md` only; re-run hook |
| `oca-checks-po` | Fix `i18n/*.po` syntax and references |
| `check-xml-unicode` | Remove BOM / bad characters in XML |

Never hand-edit `README.rst` or `static/description/index.html` when `oca-gen-addon-readme` is configured.

---

## CI-specific (OCA)

| Check | Fix |
|-------|-----|
| test with OCB / Odoo | Fix failing tests or install errors in module |
| runboat/build | Read Runboat log — usually manifest, data XML, or missing dependency |
| codecov | Add tests for new/changed Python lines |

For PR CI loops with batched pushes, see **odoo-module-migrate** → `references/pr-ci.md`.
