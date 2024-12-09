{
    "name": "wiyiya",
    "author":"Aungmoewai",
    "installed_version": "1.0",
    "category": "Sales",
    "license" : 'LGPL-3',
    "summary": """Adding user department field selection in Sales Order,User Setting and adding rule for Department Document Only """,
    "depends": ["base", "sale", "hr"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/res_user.xml",
        "views/sale_order.xml",
    ],
    "installable": True,
    "application": False,
}
