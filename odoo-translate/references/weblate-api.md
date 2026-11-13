# OCA Weblate REST API

Base URL: `https://translation.odoo-community.org/api/`  
Docs: https://docs.weblate.org/en/latest/api.html  

## Token (do not paste into chat)

1. Sign in at https://translation.odoo-community.org (GitHub login).  
2. Open your **profile** → **API access** / **API key** (user settings).  
3. Create or copy your personal token (often prefixed `wlu_`).  
4. Store it in the environment (never commit it):

```bash
export WEBLATE_TOKEN='wlu_…'          # preferred
# or
export WEBLATE_API_KEY='wlu_…'
```

Optional overrides:

```bash
export WEBLATE_URL='https://translation.odoo-community.org'
```

Auth header: `Authorization: Token $WEBLATE_TOKEN`

```bash
TOKEN="${WEBLATE_TOKEN:-$WEBLATE_API_KEY}"
curl -sS -H "Authorization: Token $TOKEN" -H "Accept: application/json" \
  "${WEBLATE_URL:-https://translation.odoo-community.org}/api/"
```

If this returns 401/403: token wrong, or account lacks language access (email **transbot@odoo-community.org**).

## Slugs

| Item | Slug pattern | Example |
|------|--------------|---------|
| Project | `{repo}-{series}` with `.` → `-` in URL path often | `field-service-18-0` or `field-service-18.0` — **discover via API** |
| Component | `{project}-{module}` | `field-service-18-0-fieldservice` |
| Language | Weblate code | `es`, `es_MX`, `fr`, `pt_BR` |

Discover (do not guess blindly):

```bash
# List / search projects
curl -sS -H "Authorization: Token $TOKEN" \
  "$WEBLATE_URL/api/projects/?page_size=100" | jq '.results[] | .slug'

# Components in a project
curl -sS -H "Authorization: Token $TOKEN" \
  "$WEBLATE_URL/api/projects/$PROJECT/components/?page_size=200" \
  | jq '.results[] | {slug, name}'

# Translation stats for language
curl -sS -H "Authorization: Token $TOKEN" \
  "$WEBLATE_URL/api/translations/$PROJECT/$COMPONENT/$LANG/"
```

## Read untranslated units

```bash
curl -sS -H "Authorization: Token $TOKEN" \
  "$WEBLATE_URL/api/translations/$PROJECT/$COMPONENT/$LANG/units/?q=state:empty&page_size=100"
```

Useful query filters (Weblate search): `state:empty`, `state:translated`, `state:needs-editing`.

## Write a translation (single unit)

```bash
# PATCH unit by id — set target string(s)
curl -sS -X PATCH \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target":["Texto traducido"],"state":20}' \
  "$WEBLATE_URL/api/units/$UNIT_ID/"
```

`state`: follow Weblate docs for the instance (translated vs needs editing). Prefer marking strings **translated** only when the target is final.

## Upload a whole `.po` (bulk)

Preferred for many strings after local edit:

```bash
curl -sS -X POST \
  -H "Authorization: Token $TOKEN" \
  -F "file=@$module/i18n/${LANG}.po" \
  -F "method=translate" \
  -F "fuzzy=process" \
  "$WEBLATE_URL/api/translations/$PROJECT/$COMPONENT/$LANG/file/"
```

`method` / conflict handling: see Weblate file upload API; default to translate/update without wiping reviewed strings.

## Create language on a component

If the language does not exist yet:

```bash
curl -sS -X POST \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"language_code\":\"$LANG\"}" \
  "$WEBLATE_URL/api/components/$PROJECT/$COMPONENT/translations/"
```

(Exact payload may use `language_code` — confirm against `/api/docs/` on the instance if POST fails.)

## Agent rules

1. Read `$WEBLATE_TOKEN` / `$WEBLATE_API_KEY` from the environment — **never** ask the user to paste the token into the chat if they can export it in the shell.  
2. Do not log the token; redact it in reports.  
3. Still respect OCA policy: no manual GitHub `.po` pushes for Weblate-managed components.  
4. After API edits, report component URL, language, units changed, remaining empty count.  
5. If API write is forbidden, fall back to preparing a `.po` for the user to upload in the UI.  
