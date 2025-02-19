# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

class PurchaseOrderLine(models.Model):
    _inherit = 'res.company'

    vendor_id = fields.Many2one("res.partner", "General Vendor")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    vendor_id = fields.Many2one("res.partner",related="company_id.vendor_id",readonly=False)