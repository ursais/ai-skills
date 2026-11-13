# Testing Odoo Modules (shared)

## Discover the project test command

```bash
grep -R "test-enable\|test_tags\|runtests\|oca.*test\|docker compose.*test" \
  .github/workflows/ Makefile tox.ini docker-compose*.yml 2>/dev/null | head -30
```

**Priority:** docker-compose → Makefile → GitHub Actions → direct `odoo` CLI.

## Default `$OCA_TEST_CMD`

```bash
export OCA_TEST_CMD="odoo --addons-path=. -d test_${module} -i ${module} \
  --stop-after-init --without-demo=all \
  && odoo --addons-path=. -d test_${module} \
  --test-enable --stop-after-init --test-tags=/${module}"
```

Single test: `--test-tags "/${module}:TestClass.test_method"`.

Upgrade path: use `-u "$module"` instead of `-i` when reproducing upgrade bugs.

## Coverage

Target **> 99%** (≥ 99.08%). Full gate: [validation-gate.md](validation-gate.md).

## Conventions (17.0+)

- Prefer `BaseCommon`; set `tracking_disable=True` on test env
- No demo data in tests — create records in `setUpClass` / `setUp`
- Mock external HTTP (`requests`)
- Short 2-line copyright headers in new test files
- Prefer **at_install** for coverage; `@post_install` only when chart/accounting setup requires it

## Layout

```
$module/tests/
├── __init__.py
└── test_*.py
```
