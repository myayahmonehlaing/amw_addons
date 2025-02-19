# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    approval_product_line_ids = fields.Many2many(
        'approval.product.line',
        'approval_product_line_purchase_rel',
        'purchase_line_id', 'approval_product_line_id',
        string='Approval Product Lines', readonly=True, copy=False)

