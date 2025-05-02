# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, Command,fields, models, _


class StockPicking(models.Model):
    _inherit = "stock.picking"

    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')