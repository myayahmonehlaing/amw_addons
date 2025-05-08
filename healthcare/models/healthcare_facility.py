from odoo import models, fields, api


class HealthcareFacility(models.Model):
    _name = 'healthcare.facility'
    _description = "The facilities list for the healthcare center"
    _order = 'name'

    # === FIELDS ===#
    code = fields.Char(string="Code", required=True, copy=False)
    name = fields.Char(string="Name",
                       store=True,
                       copy=True,
                       required=True)
    warehouse_id = fields.Many2one("stock.warehouse", string="Warehouse", required=True)

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
