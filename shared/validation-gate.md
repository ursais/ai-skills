# OCA Validation Gate (shared)

Used by **odoo-migrate**, **odoo-dev**, and **odoo-fix**.

Run before **every** `git commit` and **every** `git push`.

```
1. pre-commit run -a                          → exit 0
2. Module tests (--test-tags=/{module})       → exit 0
3. Python coverage on $module/*.py            → > 99% (check: ≥ 99.08%)
4. git commit / git push
```

If steps 1–3 modify files, stage and **restart from step 1**.

**Never** commit or push on pre-commit-only or tests-only green when the module has Python logic.

**Commit trailers:** never `Co-authored-by: Cursor …` — use `Assisted-by` instead ([git-commit.md](git-commit.md)).

## Loop

```bash
while ! pre-commit run -a; do echo "Fix pre-commit, stage, retry..."; done
while ! eval "$OCA_TEST_CMD"; do echo "Fix tests, retry..."; done

python3 -m coverage run --source="$module" $OCA_TEST_CMD
python3 -m coverage report --include="*/${module}/*" --omit="*/__manifest__.py"
python3 -m coverage report --include="*/${module}/*" --omit="*/__manifest__.py" \
  | python3 -c "
import sys
for line in sys.stdin:
    if line.startswith('TOTAL'):
        pct = float(line.split()[-1].rstrip('%'))
        print(f'Coverage: {pct}% (must be > 99%, minimum 99.08%)')
        sys.exit(0 if pct >= 99.08 else 1)
sys.exit('No TOTAL line in coverage report')
"
```

Use `coverage report -m` to list uncovered lines; add tests until the gate passes.
See [testing.md](testing.md) to discover `$OCA_TEST_CMD`.

## Coverage skip (rare)

Only when `$module/**/*.py` has **no** executable logic beyond empty `__init__.py`.
Document the reason in the final report. **codecov/patch** fails if logic exists untested.

## Interim vs final

During WIP, `pre-commit run -a || true` is OK. The gate above is **final** — never commit or
push until all three steps pass without `|| true`.
