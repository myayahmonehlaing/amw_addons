from  odoo import  models,fields,api

class PurchaseOrder(models.Model):
    _inherit="purchase.order"

    department_id = fields.Many2one(
        "hr.department",
        string="Department",
        compute="_compute_department",
        store=True,
        readonly=False
    )
    @api.depends("user_id", "user_id.department_id")
    def _compute_department(self):
        """
        Compute and store the department_id based on the user_id's department.
        """
        for record in self:
            if record.user_id and record.user_id.department_id:
                # Set department_id to the user's department
                record.department_id = record.user_id.department_id
            else:
                # Clear the department_id if no department is assigned
                record.department_id = False