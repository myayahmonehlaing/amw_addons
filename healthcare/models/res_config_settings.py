from odoo import fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_and_payment = fields.Boolean(
        string="Create invoice and payment",
        config_parameter='charm_ehr.invoice_and_payment'
    )
