from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    #To add new field for the relation of healthcare bill to show the smart button in the billing form
    bill_ids=fields.Many2one('healthcare.billing',string="Bill")

    def _create_invoices(self, grouped=False, final=False, date=None):
        invoice=super()._create_invoices()
        invoice.update({
            'bill_ids': self.bill_ids,
        })
        return invoice
