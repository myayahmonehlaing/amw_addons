# -*- coding: utf-8 -*-
{
    'name': "SME Approval",

    'summary': "SME Approval",

    'description': """
       Approval
    """,

    'author': "SME Intellect",
    'website': "https://www.smeintellect.com",

    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase','approvals','approvals_purchase'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'views/purchase_order_view.xml',
        'wizard/purchase_apporval_request_view.xml',
        'views/account_move_view.xml',
        'views/stock_picking_view.xml',
        'views/account_request_views.xml',
        'views/res_config_settings_views.xml',
    ],
    "license": "AGPL-3",
    "applications": True,
    "installable": True,
    "auto_install": False,
}
