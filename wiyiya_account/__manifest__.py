# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Wiyiya Account",

    'summary': """
           Accounting """,

    'description': """
        Accounting
        """,

    'author': "SME Intellect Co. Ltd",
    'website': "https://www.smeintellect.com/",
    'category': 'Accounting Management',
    'version': '0.1',
    'depends': ['account','hr_expense','base','hr'],
    'data': [
        'security/security.xml',
        'views/account_move_view.xml',
        'views/hr_expense_sheet_view.xml',
        'views/account_payment_view.xml',

    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
