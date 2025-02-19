# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, Command,fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    move_attachment_ids = fields.Many2many('ir.attachment', string='Attachments')