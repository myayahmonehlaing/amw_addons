from email.policy import default

from odoo import models, fields, api, _


class SaleContractLine(models.Model):
    _name = 'sale.contract.line'
    _inherit = ['mail.thread']
    _description = "Sales Contract Line"

    contract_id = fields.Many2one(
        comodel_name='sale.contract',
        string="Contract Reference",
        required=True, ondelete='cascade', index=True, copy=False)

    name = fields.Text(
        string="Description",
        compute='_compute_name',
        store=True, readonly=False, required=True, precompute=True)

    product_id = fields.Many2one(
        comodel_name='product.product',
        string="Product",
        tracking=True,
        change_default=True, ondelete='restrict', index='btree_not_null',
        domain="[('sale_ok', '=', True)]")

    uom_id = fields.Many2one(
        comodel_name='uom.uom',
        compute="_compute_product_uom_id",
        string="Unit of Measure",
        store=True, readonly=False, ondelete='restrict',
        domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(
        comodel_name='uom.category',
        related='product_id.uom_id.category_id',
    )

    # Total Quantity
    quantity = fields.Float(
        string="Quantity",
        tracking=True,
        digits='Product Unit of Measure', default=1.0,
        store=True, readonly=False, required=True)

    # Saled quantity
    sale_quantity = fields.Float(
        string="Sale Quantity",
        default=0,
        store=True,
    )
    # Remaining to sell quantity
    qty_to_sale = fields.Float(
        string="Quantity To Sale",
        compute="_compute_remaining_qty_to_sale",
        store=True,
    )
    unit_price = fields.Float(
        string="Unit Price",
        tracking=True,
        digits='Product Price',
        store=True, readonly=False, required=True, )

    subtotal = fields.Float(
        string="Subtotal",
        compute='_compute_amount',
        store=True)

    company_id = fields.Many2one(
        related='contract_id.company_id',
        store=True, index=True, precompute=True)

    order_lines = fields.Many2many(
        comodel_name="sale.order.line",
        string="Order lines",
    )

    @api.depends('product_id')
    def _compute_name(self):
        for line in self:
            if not line.product_id:
                continue

            lang = line.contract_id._get_lang()
            if lang != self.env.lang:
                line = line.with_context(lang=lang)

            if line.product_id:
                line.name = line._get_sale_contract_line_multiline_description_sale()
                continue

    def _get_sale_contract_line_multiline_description_sale(self):
        description = (
            self.product_id.get_product_multiline_description_sale()
        )
        return description

    def action_add_from_catalog(self):
        return True

    @api.depends('quantity', 'unit_price')
    def _compute_amount(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price

    @api.depends('product_id')
    def _compute_product_uom_id(self):
        for line in self:
            line.uom_id = line.product_id.uom_po_id

    @api.depends('quantity')
    def _compute_remaining_qty_to_sale(self):
        for line in self:
            line.qty_to_sale=line.quantity-line.sale_quantity

    @api.model
    def write(self, vals):
        # Track changes
        for record in self:
            tracked_fields = ['quantity', 'product_id', 'unit_price']
            changes = []
            for field in tracked_fields:
                if field in vals and vals[field] != record[field]:
                    old_value = record[field]
                    new_value = vals[field]
                    changes.append(
                        f"{field}: {old_value} → {new_value}"
                    )

            # Post changes to parent sale.contract chatter
            if changes and record.contract_id:
                message = f"Changes in contract line:\n" + "\n".join(changes)
                record.contract_id.message_post(body=message)

        return super(SaleContractLine, self).write(vals)

