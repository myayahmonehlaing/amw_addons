{
    "name": "Contract",
    "author": "Aungmoewai",
    "installed_version": "1.0",
    "category": "Sales",
    "license": 'LGPL-3',
    "summary": """
    Contract with company or user to sell our product with the desire quantity.
    If in the sale order user selected the field of the contract name, the products list of sale order lines are show with the given price.
    user can buy with the defined amount of product , and remain the contract order with the quantity .
    """,
    "depends": ["base", "sale", "mail"],
    "data": [
        # report
        "report/contract_report_views.xml",

        # menu view
        "views/sale_menus.xml",

        #Normal view
        "views/sale_contract_views.xml",
        "views/sale_order_views.xml",

        "security/ir.model.access.csv",
        "security/security.xml",
        "security/res_groups.xml",

        # print pdf
        "report/ir_action_report_template.xml",
        "report/ir_actions_report.xml",

    ],
    "installable": True,
    "application": False,
}
