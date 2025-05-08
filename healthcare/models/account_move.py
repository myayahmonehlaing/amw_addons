from odoo import fields,models,api

class AccountMove(models.Model):
    _inherit = 'account.move'

    #To add new field for the relation of healthcare bill to show the smart button in the billing form
    bill_ids=fields.Many2one('healthcare.billing',string="Bill")
