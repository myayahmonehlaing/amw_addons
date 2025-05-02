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
    # ===== SQL Constraint =====#

    # ===== method =======#
    @api.onchange("default")
    def change_default(self):
        """
        if one status line is check to default :
        it will be the check and other check value to false
        """
        if self.default:
            other_records = self.env["healthcare.appointment.status"].search(
                [("name", "!=", self.name), ("default", "=", True)]
            )
            for record in other_records:
                record.default = False
