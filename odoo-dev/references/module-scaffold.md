# Module Scaffold

Create a new addon under `$module/` on branch `${target_ver}-add-${module}-${ISSUE_NUMBER}`.

## Standard layout

```
$module/
├── __init__.py
├── __manifest__.py
├── pyproject.toml
├── models/
│   ├── __init__.py
│   └── my_model.py
├── views/
│   └── my_model_views.xml
├── security/
│   └── ir.model.access.csv
├── data/                    # optional — sequences, cron, mail templates
├── demo/                    # optional — one XML per model
├── readme/
│   ├── DESCRIPTION.md
│   ├── CONFIGURE.md
│   ├── USAGE.md
│   └── CONTRIBUTORS.md
├── static/description/
│   └── icon.png             # copy from reference module
└── tests/
    ├── __init__.py
    └── test_my_model.py
```

Add `wizards/`, `reports/`, `controllers/` only when the issue requires them.

## `__manifest__.py` template

```python
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Human Readable Name",
    "version": "${target_ver}.1.0.0",
    "author": "Gray Matter Logic, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/${repo}",
    "license": "AGPL-3",
    "category": "Category From Reference Module",
    "development_status": "Beta",
    "maintainers": ["max3903"],
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/my_model_views.xml",
    ],
    "demo": [],
    "installable": True,
}
```

- Set `maintainers` to the author’s GitHub login (or maintainers named in the issue)
- Match `category`, `depends`, and `development_status` style from a reference module on `origin/$target_ver`
- Order `data` keys: security → data → views → menus → reports
- List each demo file separately in `"demo"` (one per model)

## `pyproject.toml`

Required in current OCA repos:

```toml
[build-system]
requires = ["whool"]
build-backend = "whool.buildapi"
```

## `__init__.py`

```python
from . import models
```

## Model stub

```python
# Copyright (C) 2026 Gray Matter Logic (<https://www.graymatterlogic.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MyModel(models.Model):
    _name = "my.model"
    _description = "My Model"

    name = fields.Char(required=True)
```

## Security minimum

`security/ir.model.access.csv`:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,1
```

Define `model_my_model` via `<record id="model_my_model" model="ir.model">` only if needed;
usually Odoo creates `model_*` XML IDs automatically from `_name` with dots → underscores.

## View minimum

```xml
<?xml version="1.0" encoding="utf-8" ?>
<odoo>
    <record id="view_my_model_tree" model="ir.ui.view">
        <field name="name">my.model.list</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <list>
                <field name="name" />
            </list>
        </field>
    </record>
</odoo>
```

Use `<list>` not `<tree>` on Odoo 18.0+.

## Install smoke test

After scaffold:

```bash
pre-commit run --files "$module/"*
odoo --addons-path=. -d test_${module} -i "$module" --stop-after-init --without-demo=all
```

Fix manifest paths and XML before building features.
