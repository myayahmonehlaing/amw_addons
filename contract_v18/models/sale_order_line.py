from odoo import models,fields,api

class SaleOrderLine(models.Model):
    _inherit='sale.order.line'

    contract_lines=fields.Many2many(
        comodel_name='sale.contract.line',
        string="Sales Contract Lines"
    )








