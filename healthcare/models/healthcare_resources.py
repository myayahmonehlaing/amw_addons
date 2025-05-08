from odoo import models, fields


class HealthcareResources(models.Model):
    _name = 'healthcare.resources'
    _description = "The resource list for the healthcare center"
    _order = 'name'

    # === FIELDS ===#
    name = fields.Char(string="Name",
                       default="Room1",
                       store=True,
                       required=True)
    facility_id = fields.Many2one("healthcare.facility", string="Facility", required=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)

    # ===== SQL Constraint =====#

    # ===== method =======#
