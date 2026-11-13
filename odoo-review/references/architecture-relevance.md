# Architecture and relevance review

Evaluate whether the **proposed solution fits the problem** — not only whether the code is correct. A PR can be green and convention-clean and still be the wrong shape.

Inspired by reviews like [OCA/field-service#1623](https://github.com/OCA/field-service/pull/1623) (etobella): a minimal change may belong in the **base module** rather than a **new addon**.

## Always answer these

1. **Problem ↔ solution fit** — Does the diff solve the stated issue/PR goal without unrelated scope?
2. **Module placement** — New addon vs extend existing/base module: is the split justified?
3. **Reuse** — Is there already an OCA/module API, mixin, or pattern that should be used instead of a parallel design?
4. **Complexity** — Is the approach proportional (new models/wizards/bridges vs a small field/method/view inherit)?
5. **Coupling** — Hard deps, cross-module leaps, or fragile overrides that will hurt upgrades?
6. **Alternatives** — Would a simpler or more standard Odoo/OCA approach work better? Say so briefly.

## New module vs base / existing module

| Prefer **extend base / existing** when | Prefer **new module** when |
|----------------------------------------|----------------------------|
| Change is small (button, field, method, view inherit) | Feature is optional for many deployments |
| Behavior is core to the host module’s domain | Extra dependency weight is undesirable for base users |
| Split mainly adds packaging overhead | Clear product boundary / separate maintainers |
| No strong optional-dependency story | Needs its own deps, security, or install footprint |

**Must-fix** when a new module adds little beyond what a few lines in the parent module would do, with no clear optional-install benefit — ask the author to justify the split or move the change.

**Suggestion** when the split is defensible but borderline — ask for rationale in the PR body.

## Other architecture smells (must-fix or suggestion by severity)

- Re-implementing what `mail`, `portal`, `base`, or a sibling OCA module already provides
- New model where a field, related, or transient wizard would suffice
- Deep `_inherit` / monkeypatch chains instead of clean extension points
- Business logic only in views/onchange with no reusable model API
- Copy-paste across modules instead of a shared mixin/utility
- Solution tied to one customer’s workflow with no generalization, presented as generic OCA

## How to report

In the PR review:

- Add a short **Architecture / relevance** subsection (or bullets under Must fix / Suggestions)
- State the conclusion: **fit** / **questionable** / **wrong placement**
- If wrong placement: concrete ask (e.g. “move into `fieldservice`” or “justify optional module in DESCRIPTION”)

Do **not** block solely on taste when the design is a normal OCA optional addon with real install-time value.
