from odoo import models, fields, api

class HealthcareBillingProducts(models.Model):
    _name = 'healthcare.billing.products'
    _description = "The billing product list for the healthcare center"

    # === FIELDS ===#
    product = fields.Many2one(
        'product.product', 'Product', check_company=True, store=True,  readonly=False,
        required=True,domain=[('type', '=', 'consu')])
    qty=fields.Float(string="Qty",required=True)
    price=fields.Float(string="Price",required=True)
    amount=fields.Float(string="Amount",compute="_compute_amount")
    billing = fields.Many2one("healthcare.billing", string="Billing")


    # ===== SQL Constraint =====#

    #===== method =======#
    @api.onchange('product')
    def onchange_product(self):
        """
        Update price and amount based on the selected product.
        """
        if self.product:
            # Set the price from the product's `list_price`
            self.price = self.product.lst_price  # `lst_price` is the list price field in the `product.product` model
            # Automatically set quantity to 1 if not provided
            if not self.qty:
                self.qty = 1
            # Calculate the amount based on qty and price
            self.amount = self.price * self.qty
        else:
            # Reset price, qty, and amount if no product is selected
            self.price = 0
            self.qty = 0
            self.amount = 0

    @api.depends('product', 'qty', 'price')
    def _compute_amount(self):
        for record in self:
            if (record.qty > 0 and record.price > 0):
                record.amount = record.qty * record.price



