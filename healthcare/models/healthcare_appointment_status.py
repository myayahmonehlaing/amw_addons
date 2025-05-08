"""
Work for Appointment Status list for check the state of the appointment
"""

from odoo import models, fields, api


class HealthcareAppointmentStatus(models.Model):
    """
    Handle for the status of appointments
    """
    _name = "healthcare.appointment.status"
    _description = "The appointment status list for the healthcare center"
    _order = "sequence"

    # === FIELDS ===#
    name = fields.Char(string="Name", copy=True, required=True)  # check in, confirm ...
    default = fields.Boolean(string="Default")
    sequence = fields.Integer("Sequence")
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)
    # ===== SQL Constraint =====#

    # ===== method =======#
    # @api.depends("default")
    # def change_default(self):
    #     """
    #     if one status line is check to default :
    #     it will be the check and other check value to false
    #     """
    #     if self.default:
    #         other_records = self.env["healthcare.appointment.status"].search(
    #             [("name", "!=", self.name), ("default", "=", True)]
    #         )
    #         for record in other_records:
    #             record.default = False
    @api.onchange('default')
    def _onchange_default(self):
        if self.default:
            for record in self.env['healthcare.appointment.status'].search([]):
                if record.id != self.id:
                    record.default = False

    @api.model
    def create(self, vals):
        if vals.get('default'):
            self.search([('default', '=', True)]).write({'default': False})
        return super().create(vals)

    def write(self, vals):
        if vals.get('default'):
            self.search([('default', '=', True), ('id', '!=', self.id)]).write({'default': False})
        return super().write(vals)