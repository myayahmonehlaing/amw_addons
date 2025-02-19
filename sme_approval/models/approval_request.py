# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.fields import Command
from odoo.tools.misc import clean_context
from odoo.tools import frozendict, format_date, float_compare, Query

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'
    _order = 'name desc'

    to_purchase = fields.Boolean(String="To Purchase",compute="_compute_to_purchase", store=True )
    request_status = fields.Selection(selection_add=[('rfq', 'RFQ Create'),('refused',)])

    @api.depends('product_line_ids.qty_to_purchase')
    def _compute_to_purchase(self):
        for approval in self:
            approval.to_purchase = sum(approval.product_line_ids.mapped('qty_to_purchase')) > 0

    def action_create_rfq(self):
        self.request_status = 'rfq'

    def _get_purchase_order_values(self):
        """ Get some values used to create a purchase order.
        Called in approval.request `action_create_purchase_orders`.

        :param vendor: a res.partner record
        :return: dict of values
        """
        self.ensure_one()
        vals = {
            'origin': self.name,
            'partner_id': self.company_id.vendor_id.id,
            # 'facility_id': self.facility_id.id,
            'company_id': self.company_id.id,
            'payment_term_id': self.company_id.vendor_id.property_supplier_payment_term_id.id,
            'fiscal_position_id':self.env['account.fiscal.position']._get_fiscal_position(self.company_id.vendor_id).id,
             'attachment_ids': [(6, 0, self.env['ir.attachment'].search([('res_model', '=', 'approval.request'), ('res_id', 'in', self.ids)]).ids   )   ],
        }

        return vals

    def action_create_purchase_orders(self):
        """ Create and/or modifier Purchase Orders. """

        self.ensure_one()
        if any(line.qty_to_purchase > 0 for line in self.product_line_ids):
            po_vals = self._get_purchase_order_values()
            purchase_order = self.env['purchase.order'].create(po_vals)
        for line in self.product_line_ids:
            if line.qty_to_purchase:
                    po_line_vals = self.env['purchase.order.line']._prepare_purchase_order_line(
                        line.product_id,
                        line.qty_to_purchase,   # yahmone@smeintellect.com
                        line.product_uom_id,
                        line.company_id,
                        line.seller_id,
                        purchase_order,
                    )
                    po_line_vals['approval_product_line_ids'] = [Command.link(line.id)] # yahmone@smeintellect.com
                    new_po_line = self.env['purchase.order.line'].create(po_line_vals)
                    line.purchase_order_line_id = new_po_line.id
                    purchase_order.order_line = [(4, new_po_line.id)]


    @api.depends('product_line_ids.purchase_order_line_id','product_line_ids.purchase_order_line_ids')
    def _compute_purchase_order_count(self):
        for request in self:

            purchases = request.product_line_ids.purchase_order_line_ids.order_id

            request.purchase_order_count = len(purchases)

    def action_open_purchase_orders(self):
        res = super().action_open_purchase_orders()
        purchase_ids = self.product_line_ids.purchase_order_line_id.order_id.ids + self.product_line_ids.purchase_order_line_ids.order_id.ids
        res['domain'] = [('id', 'in', purchase_ids)]
        return res


class ApprovalProductLine(models.Model):
    _inherit = 'approval.product.line'

    product_uom_id = fields.Many2one(
        'uom.uom', string="Unit of Measure",
        compute="_compute_product_uom_id", store=True, readonly=False, precompute=True,
        domain="[('category_id', '=', product_uom_category_id)]")
    qty_to_purchase = fields.Float(string="Quantity To Purchase",compute="_compute_qty_to_purchase",
                                   inverse="_inverse_qty_to_purchase",store=True, digits='Product Unit of Measure',)
    qty_purchased = fields.Float(string="Purchased Qty",
        compute="_compute_qty_purchased",store=True, digits='Product Unit of Measure',)

    purchase_order_line_ids = fields.Many2many(
        comodel_name='purchase.order.line',
        relation= 'approval_product_line_purchase_rel', column1='approval_product_line_id', column2='purchase_line_id',
        string='Purchase Order Lines', readonly=True, copy=False)


    @api.depends('product_id')
    def _compute_product_uom_id(self):
        for line in self:
            line.product_uom_id = line.product_id.uom_po_id

    @api.constrains('qty_to_purchase','quantity')
    def _check_qty_to_purchase(self):
        for line in self:
            decimal_precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            if float_compare( line.quantity - line.qty_purchased, line.qty_to_purchase, precision_digits=decimal_precision)  < 0:
                raise ValidationError("The remaining quantity (quantity - qty_purchased) cannot be less than the quantity to purchase.")


    # def _get_purchase_order_values(self, vendor):
    #     vals =  super()._get_purchase_order_values(vendor)
    #     if self.approval_request_id.facility_id:
    #         vals['facility_id'] = self.approval_request_id.facility_id.id
    #         vals['partner_id'] = self.company_id.vendor_id.id
    #     return vals

    @api.depends('quantity','qty_purchased','approval_request_id.request_status',
                 'purchase_order_line_ids.order_id.state','purchase_order_line_ids.product_qty')
    def _compute_qty_to_purchase(self):
        for line in self:
            if line.approval_request_id.request_status == 'rfq':
                    line.qty_to_purchase = line.quantity - line.qty_purchased
            else:
                line.qty_to_purchase = 0

    def _inverse_qty_to_purchase(self):
        pass

    @api.depends('quantity','purchase_order_line_ids.order_id.state', 'purchase_order_line_ids.product_qty')
    def _compute_qty_purchased(self):
        """
        Compute the quantity invoiced. If case of a refund, the quantity invoiced is decreased. Note
        that this is the case only if the refund is generated from the SO and that is intentional: if
        a refund made would automatically decrease the invoiced quantity, then there is a risk of reinvoicing
        it automatically, which may not be wanted at all. That's why the refund has to be created from the SO
        """
        for line in self:
            qty_purchased = 0.0
            for purchase_line in line.purchase_order_line_ids:
                if purchase_line.order_id.state != 'cancel':
                        qty_purchased += purchase_line.product_uom._compute_quantity(purchase_line.product_qty, line.product_uom_id)
            # if line.purchase_order_line_id and line.purchase_order_line_id.order_id.state !='cancel':
            #     purchase_line = line.purchase_order_line_id
            #     qty_purchased += purchase_line.product_uom._compute_quantity(purchase_line.product_qty,
            #                                                                  line.product_uom_id)

            line.qty_purchased = qty_purchased