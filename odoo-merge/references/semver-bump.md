# Semver bump for `/ocabot merge`

OCA ocabot expects exactly one of:

```text
/ocabot merge patch
/ocabot merge minor
/ocabot merge major
```

Choose from what operators must do after deploy — inspect the **PR diff** for schema/data changes and for a migration script when needed.

## Definitions (authoritative)

| Bump | Meaning |
|------|---------|
| **patch** | A **server restart** is enough for the changes to take effect |
| **minor** | The **module needs to be upgraded** |
| **major** | The changes need a **migration script that is provided in the pull request** |

## How to classify

### patch

Restart-only: Python/JS/XML that loads on restart without `-u`, no new/changed stored fields that require module update, no end-user data migration.

Examples: pure bug fixes in methods, report QWeb, controllers, most view-only XML, tests, CI, i18n, docs.

### minor

Module upgrade (`-u`) required: new fields/models, manifest data/security CSV changes, changed `noupdate` XML that needs update, new dependencies — but **no** custom migration script in the PR.

### major

Breaking or data-moving changes that ship an explicit migration (e.g. `migrations/<version>/pre-migrate.py`, `post-migrate.py`, or equivalent scripts **in this PR**). If a migration script is required but **missing**, do **not** post `/ocabot merge major` — block and ask the author to add it (or confirm bump).

## Ambiguity

| Situation | Prefer |
|-----------|--------|
| Code-only fix, no ORM schema / data XML needing `-u` | `patch` |
| New field/model / access rights / data XML needing `-u`, no migration script | `minor` |
| PR includes a migration script for the change | `major` |
| Schema/data change that clearly needs a migration script but none is in the PR | **Block** — do not merge until script exists or bump is clarified |
| Unsure between patch and minor | Prefer `minor` if anything in `__manifest__` data/demo/security or model fields changed |

State the chosen bump and one-line rationale (restart / upgrade / migration script path) in the user report.
