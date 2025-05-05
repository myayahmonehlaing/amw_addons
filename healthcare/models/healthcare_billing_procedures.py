from odoo import models, fields, api

class HealthcareBillingProcedures(models.Model):
    _name = 'healthcare.billing.procedures'
    _description = "The billing procedure list for the healthcare center"

    # === FIELDS ===#
    product_id = fields.Many2one(
        'product.product', 'Description', check_company=True, store=True,  readonly=False,
        required=True, domain=[('type', '=', 'service')])
    qty=fields.Float(string="Qty",required=True)
    unit_price=fields.Float(string="Unit Price",required=True)
    amount=fields.Float(string="Amount",compute="_compute_amount")
    billing_id =fields.Many2one("healthcare.billing",required=True)


    # ===== SQL Constraint =====#

    #===== method =======#
    @api.onchange('product_id')
    def onchange_product(self):
        """
        Update price and amount based on the selected product.
        """
        if self.product_id:
            # Set the price from the product's `list_price`
            self.unit_price = self.product_id.lst_price  # `lst_price` is the list price field in the `product.product` model
            # Automatically set quantity to 1 if not provided
            if not self.qty:
                self.qty = 1
            # Calculate the amount based on qty and price
            self.amount = self.unit_price * self.qty
        else:
            # Reset price, qty, and amount if no product is selected
            self.unit_price = 0
            self.qty = 0
            self.amount = 0

    @api.depends('product_id','qty','unit_price')
    def _compute_amount(self):
        for record in self:
            if(record.qty>0 and record.unit_price>0):
                record.amount = record.qty * record.unit_price

