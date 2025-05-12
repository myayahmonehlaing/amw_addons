from odoo import models, fields

class HealthcareProviders(models.Model):
    _name = 'healthcare.providers'
    _description = "The provider list for the healthcare center"
    _order='name'

    # === FIELDS ===#
    name = fields.Char(string="Name",
                       store=True,
                       required=True)
    speciality_id = fields.Many2one("healthcare.providers.speciality", string="Speciality",required=True)
    qualifications = fields.Text('Qualifications')
    visit_type_id = fields.Many2one("healthcare.visit.types", string="Visit Type",required=True)
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
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)
 
    # ===== SQL Constraint =====#

    # ===== method =======#
