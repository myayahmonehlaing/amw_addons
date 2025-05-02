from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    department_id = fields.Many2one("hr.department", string="Department")
