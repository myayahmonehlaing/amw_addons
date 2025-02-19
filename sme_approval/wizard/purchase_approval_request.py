from odoo import api, fields, models, Command, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import frozendict, format_date, float_compare, Query

class PurchaseApprovalRequest(models.TransientModel):
    _name = "purchase.approval.request"


    approval_request_ids = fields.Many2many("approval.request", string="Approval Request", domain=[('request_status', '=', 'rfq'),
                                                                                            ('to_purchase','=', True),  ])

    purchase_approval_product_line_ids = fields.One2many('purchase.approval.request.line', 'wizard_id')
    available_approval_request_ids = fields.Many2many(
        'approval.request',
        compute='_compute_available_approval_request_ids',
    )

    def _compute_available_approval_request_ids(self):
        for a in self:
            journal_type = a.invoice_filter_type_domain or 'general'
            company = a.company_id or self.env.company
            a.available_approval_request_ids = self.env['approval.request'].search([
               
                ('type', '=', journal_type),
            ])



    def action_create_purchase_order_line(self):
        purchase_id = self.env['purchase.order'].browse(self.env.context.get('active_ids'))
        po_line_vals ={}
        requests =  self.env['approval.request']
        for line in self.purchase_approval_product_line_ids:
            if line.qty_to_purchase > 0:
                requests +=line.approval_request_id
                po_line_vals = self.env['purchase.order.line']._prepare_purchase_order_line(
                    line.product_id,
                    line.qty_to_purchase,  # yahmone@smeintellect.com
                    line.product_uom_id,
                    line.approval_product_line_id.company_id,
                    line.approval_product_line_id.seller_id,
                    purchase_id,
                )
                po_line_vals['approval_product_line_ids'] = [Command.link(line.approval_product_line_id.id)]  # yahmone@smeintellect.com
                self.env['purchase.order.line'].create(po_line_vals)

        if requests:
            origin = ''
            if purchase_id.origin:
                # missing_origin =  set(purchase_id.origin.split(', '))
                # if missing_origin:
                    origin = purchase_id.origin + ', ' + ', '.join(set(requests.mapped('name')))
            else:
                origin = ', '.join(set(requests.mapped('name')))

            purchase_id.write({
                'attachment_ids':  [(4, attachment ) for attachment in self.env['ir.attachment'].search([('res_model', '=', 'approval.request'), ('res_id', 'in', requests.ids)]).ids ],
                'origin': origin
            })


        return True


    @api.onchange('approval_request_ids')
    def _onchange_approval_request_ids(self):
        existing_ids = set(self.purchase_approval_product_line_ids.mapped('approval_product_line_id'))
        # Filter and create new commands for non-duplicate lines
        self.purchase_approval_product_line_ids = [
            Command.create({
                'product_id': line.product_id,
                'product_uom_id': line.product_uom_id,
                'quantity': line.quantity,
                'qty_purchased': line.qty_purchased,
                'qty_to_purchase': line.qty_to_purchase,
                'approval_product_line_id': line,
                'approval_request_id': line.approval_request_id,

            })
            for line in self.approval_request_ids.mapped('product_line_ids')
            if line._origin not in existing_ids and line.qty_to_purchase > 0   # Exclude duplicates
        ]



class PurchaseApprovalRequestLine(models.TransientModel):
    _name = "purchase.approval.request.line"

    wizard_id = fields.Many2one('purchase.approval.request',required=True)

    product_id = fields.Many2one('product.product', string="Products", )
    product_uom_id = fields.Many2one(
        'uom.uom', string="Unit of Measure",

    )
    quantity = fields.Float("Quantity",)
    qty_purchased = fields.Float("Purchased Qty", )
    qty_to_purchase = fields.Float("Quantity To Purchase", )
    approval_product_line_id = fields.Many2one('approval.product.line')
    approval_request_id = fields.Many2one('approval.request' )

    @api.constrains('qty_to_purchase','quantity')
    def _check_qty_to_purchase(self):
        for line in self:
            decimal_precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            if float_compare( line.quantity - line.qty_purchased, line.qty_to_purchase, precision_digits=decimal_precision)  < 0:
                raise ValidationError("The remaining quantity (quantity - qty_purchased) cannot be less than the quantity to purchase.")


