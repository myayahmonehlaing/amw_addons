{
    "name": "SaleReport",
    "author": "Aungmoewai",
    "installed_version": "1.0",
    "category": "Sales",
    "license": 'LGPL-3',
    "summary": """
    Adding new menu of sale report under the report of sale to print with pdf or xls file between the defined duration date of sale order
    """,
    "depends": ["base", "sale"],
    "data": [
        "views/sale_report_wizard_views_form.xml",
        "views/sale_menus.xml",

        "report/ir_actions_report_templates.xml",

        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": False,
}
