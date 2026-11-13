# Contributor profile

Edit this file once. After install it lives at `~/.cursor/skills/shared/contributor.md`.

Skills that push or write new copyright read it before they start. If a required value below is still a `YOUR_*` placeholder, stop and ask the user to edit this file. Do not guess an organization, name, or email.

`maintainer` and `human_tester` may stay blank. Blank means the authenticated GitHub user (`gh api user -q .login`).

| Key | Required | Value |
|-----|----------|--------|
| `fork_owner` | Before any push or rebase | `YOUR_GITHUB_ORG` |
| `author_name` | Before new copyright | `YOUR_NAME` |
| `author_url` | Before new copyright | `YOUR_URL` |
| `author_email` | Before new copyright | `YOUR_EMAIL` |
| `maintainer` | No | |
| `human_tester` | No | |
| `helpdesk_base` | No | |

## fork_owner

GitHub user or organization that owns the fork of each OCA repository. All workflow pushes go to `$fork_owner/$repo`. Never push those branches to `OCA`.

When the fork does not exist yet: if `fork_owner` is an organization, create it with the `organization` field. If `fork_owner` is a user, omit `organization`.

## maintainer

GitHub login stored in `__manifest__.py` `maintainers` and used as the default pull-request assignee. Blank uses the authenticated user.

## human_tester

GitHub login `odoo-review` assigns when a pull request is ready for human testing. Blank uses the authenticated user.

## author_name, author_url, author_email

Copyright header and `CONTRIBUTORS.md` line on files you add. Leave existing authors and copyright years as they are.

`author_url` includes the scheme, for example `https://example.com`.

## helpdesk_base

Optional URL prefix. When set, `odoo-fix` accepts a ticket whose URL starts with it, as well as a GitHub issue. When blank, `odoo-fix` accepts GitHub issues only.
