from odoo import models, fields, api, _


class HealthcareLabs(models.Model):
    _name = 'healthcare.labs'
    _description = "The labs list for the healthcare center"
    _order = 'name desc'

    # === FIELDS ===#
    name = fields.Char(string="Name", copy=False, default=lambda self: _('New'),
                       store=True,
                       readonly=True)  # need to add compute #LB00001
    patient_id = fields.Many2one("healthcare.patients", string="Patient", required=True)
    provider_id = fields.Many2one("healthcare.providers", string="Provider", required=True)
    date = fields.Date(string="Date", required=True)
    results = fields.Text(string="Results", copy=True)
    diagnosis = fields.Text(string="Diagnosis", copy=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)

    # ===== SQL Constraint =====#

    # ===== method =======#
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('healthcare.labs.code') or 'New'
        return super(HealthcareLabs, self).create(vals)
