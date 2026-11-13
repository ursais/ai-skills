# OCA Weblate

Service: **https://translation.odoo-community.org**  
OCA overview: https://www.odoo-community.org/resources/translate  

## Access

1. Register with your **GitHub** login on Weblate.  
2. Email **transbot@odoo-community.org** with:
   - your GitHub username  
   - language(s) you want to translate to  
3. Wait until language permissions are granted, then translate.
4. For agent automation: create an **API token** in your Weblate profile and `export WEBLATE_TOKEN=…` (see [weblate-api.md](weblate-api.md)). Never paste the token into chat.

## Project / component layout

| Concept | Pattern | Example |
|---------|---------|---------|
| Project | `{oca-repo}-{series}` | `field-service-18.0` |
| Component | `{oca-repo}-{series}-{module}` | `field-service-18.0-fieldservice` |
| UI URL | `/projects/{project}/{component}/` | …/projects/field-service-18-0/field-service-18-0-fieldservice/ |

Notes:

- One Weblate **project** per GitHub repo + branch.  
- One **component** per addon that has a `.pot`.  
- Weblate discovers new projects/addons periodically; a missing component usually means no `.pot` on that series branch yet (CI `MAKEPOT` / first push with template).  
- Hyphenation in URLs may normalize dots (`18.0` → `18-0`); use the UI search if unsure.

## Translator workflow

1. Open the component → language (or **Start new translation**).  
2. Translate in the Weblate UI; use context / sibling strings for consistency.  
3. There is generally **no review gate** on OCA Weblate — translate carefully.  
4. Prefer Weblate’s glossary / automatic suggestions when helpful.  
5. Offline work: export/translate → **Upload** translation file in Weblate (do not push `.po` to GitHub yourself).

Weblate user guide: https://docs.weblate.org/en/latest/user/translating.html

## Automation (do not fight the bot)

Typical OCA flow:

| Event | Who |
|-------|-----|
| Regenerate `.pot` on series branch | OCA CI (`MAKEPOT` / post-merge jobs) |
| Pull `.pot` into Weblate | Weblate (periodic) |
| Update `.po` for new/removed terms | Weblate (`msgmerge`-style) |
| Commit/push translations to GitHub | Weblate bot (delayed; often ~hourly for aged changes) |

**Do**

- Translate (or upload) on Weblate  
- Fix source strings in Python/XML/JS via a normal module PR; let CI refresh `.pot`  
- Wait for the bot after large translation batches  

**Don't**

- Manually commit/push Weblate-managed `.po` files to OCA main branches  
- Force-push over `Translated using Weblate` commits  
- Create `en.po`  
- Expect instant GitHub reflection — allow bot lag  

## When Weblate is not enough

Use [i18n-files.md](i18n-files.md) when:

- The addon is **not** on OCA / not connected to this Weblate  
- You only need a local `.pot` refresh on a feature branch before CI  
- The component is missing and you must add `${module}.pot` so Weblate can pick it up after merge  
