from odoo import models, fields


class HealthcareResources(models.Model):
    _name = 'healthcare.resources'
    _description = "The resource list for the healthcare center"

    # === FIELDS ===#
    name = fields.Char(string="Name",
                       default="Room1",
                       store=True,
                       required=True)
    facility_id = fields.Many2one("healthcare.facility",string="Facility",required=True)

    # ===== SQL Constraint =====#

    #===== method =======#




