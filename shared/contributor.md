# Contributor profile

Edit this file once. After install it lives at `~/.cursor/skills/shared/contributor.md`.

Skills that push or write new copyright read it before they start. If a required value below is still a `YOUR_*` placeholder, stop and ask the user to edit this file. Do not guess an organization, name, or email.

`maintainer` may stay blank. Blank means the authenticated GitHub user (`gh api user -q .login`). GitHub assignees are not taken from this file. Only `odoo-assign` sets them.

| Key | Required | Value |
|-----|----------|--------|
| `fork_owner` | Before any push or rebase | `YOUR_GITHUB_ORG` |
| `author_name` | Before new copyright | `YOUR_NAME` |
| `author_url` | Before new copyright | `YOUR_URL` |
| `author_email` | Before new copyright | `YOUR_EMAIL` |
| `maintainer` | No | |

## fork_owner

GitHub user or organization that owns the fork of each OCA repository. All workflow pushes go to `$fork_owner/$repo`. Never push those branches to `OCA`.

When the fork does not exist yet: if `fork_owner` is an organization, create it with the `organization` field. If `fork_owner` is a user, omit `organization`.

## maintainer

GitHub login stored in `__manifest__.py` `maintainers` on modules you create. Blank uses the authenticated user. This is not the assignee of an existing OCA issue or pull request.

## author_name, author_url, author_email

Copyright header and `CONTRIBUTORS.md` line on files you add. Leave existing authors and copyright years as they are.

`author_url` includes the scheme, for example `https://example.com`.
