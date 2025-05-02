from odoo import models, fields

class HealthcareProviders(models.Model):
    _name = 'healthcare.providers'
    _description = "The provider list for the healthcare center"

    # === FIELDS ===#
    name = fields.Char(string="Name",
                       store=True,
                       required=True)
    visit_type = fields.Many2one("healthcare.visit.types", string="Visit Type",required=True)
    email = fields.Char(string="Email",required=True)
    phone = fields.Char(string="Phone",required=True)

    # Address fields
    street = fields.Char('Street', readonly=False, store=True)
    street2 = fields.Char('Street2', readonly=False, store=True)
    zip = fields.Char('Zip', change_default=True, readonly=False, store=True)
    city = fields.Char('City', readonly=False, store=True)
    state_id = fields.Many2one(
        "res.country.state", string='State', readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country', readonly=False, store=True)
    # ===== SQL Constraint =====#

    # ===== method =======#
