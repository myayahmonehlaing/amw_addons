from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

# create a field of department that are get from hr.department by relational Many to one and get the stored data of department from user form by
# calculation _compute_department method
    department_id = fields.Many2one(
        "hr.department",
        string="Department",
        compute="_compute_department",
        store=True,
        readonly=False
    )
    
# Check current user department from user and get it
    @api.depends("user_id","user_id.department_id")
    def _compute_department(self):
        for record in self:
            if record.user_id and record.user_id.department_id:
                # Set dep_id1 to the user's department
                record.department_id = record.user_id.department_id
            else:
                # Clear dep_id1 if there's no department
                record.department_id = True
