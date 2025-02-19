# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, Command,fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # partner_id = fields.Many2one('res.partner', domain="[('is_vendor', '=', True)]")
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    is_subcontract = fields.Boolean("Is Subcontract?")

    def button_approval_request(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.approval.request',
            'view_mode': 'form',
            'target': 'new',
        }

    def _prepare_invoice(self):
        result = super()._prepare_invoice()
        result['move_attachment_ids'] = [(6, 0, self.attachment_ids.ids )]
        return result

    def _prepare_picking(self):
        result = super()._prepare_picking()
        result['attachment_ids'] = [(6, 0, self.attachment_ids.ids)]
        return result





class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    expired_date = fields.Date("Expired Date")
    procurement_note = fields.Char("Procurement Note")