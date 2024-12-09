# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api,Command, fields, models, _

class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    advance_id = fields.Many2one("account.move","Advance")

    def _prepare_move_vals(self):
        """Overwrite to update date and invoice date of accout_move

        Returns:
            dict: values of move to create
        """
        res = super()._prepare_move_vals()
        res['invoice_date'] = self.accounting_date
        res['date'] = self.accounting_date
        return res
