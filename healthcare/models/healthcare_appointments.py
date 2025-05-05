from odoo import models, fields, api


APPOINTMENT_CATEGORY = [
    ("appointment", "Appointment"),
    ("other_event", "Other Event"),
    ("waiting_list", "Waiting List"),
]
APPOINTMENT_MODE = [
    ("in_person", "In Person"),
    ("phone_call", "Phone Call"),
    ("video_consult", "Video Consult"),
]


class HealthcareAppointments(models.Model):
    _name = "healthcare.appointment"
    _inherit = ["mail.thread", "mail.activity.mixin", "analytic.mixin"]
    _description = "The appointment list for the healthcare center"

    # === FIELDS ===#
    name = fields.Char(
        string="Name",
        copy=False,
        default=lambda self: self._compute_name(),
        store=True,
        readonly=True,
    )
    facility_id = fields.Many2one(
        "healthcare.facility", string="Facility", required=True, tracking=True
    )  # need to add compute #IM00001
    category = fields.Selection(
        selection=APPOINTMENT_CATEGORY, string="Category", required=True, tracking=True
    )
    patient_id = fields.Many2one(
        "healthcare.patients",
        string="Patient",
        required=True,
        tracking=True,
    )
    provider_id = fields.Many2one(
        "healthcare.providers", string="Provider", required=True, tracking=True
    )
    status = fields.Many2one(
        "healthcare.appointment.status",
        string="Status",
        default=lambda self: self._get_default_status(),
        required=True,
        tracking=True,
    )
    visit_type_id = fields.Many2one(
        "healthcare.visit.types", string="Visit Type", required=True, tracking=True
    )
    resource_id = fields.Many2one(
        "healthcare.resources", string="Resource", required=True, tracking=True
    )
    appointment_mode = fields.Selection(
        selection=APPOINTMENT_MODE,
        string="Appointment Mode",
        required=True,
        tracking=True,
    )
    date = fields.Date(
        string="Date", default=fields.Date.today, required=True, tracking=True
    )
    reason = fields.Text(string="Reason", tracking=True)
    message_to_patient = fields.Text(string="Message To Patient", tracking=True)

    # ===== SQL Constraint =====#

    # ===== method =======#
    @api.model
    def _compute_name(self):

        # Search for the last appointment name in the database
        last_appointment = self.env["healthcare.appointment"].search(
            [], order="name desc", limit=1
        )
        if last_appointment and last_appointment.name:
            # Extract the numeric part and increment it
            last_number = int(last_appointment.name[1:])  # Assumes format Axxxxx
            new_number = last_number + 1
        else:
            # Start from 1 if no records exist
            new_number = 1

        # Format the new billing number as Axxxxx
        return f"A{str(new_number).zfill(5)}"

    @api.model
    def _get_default_status(self):
        return self.env["healthcare.appointment.status"].search(
            [("default", "=", True)], limit=1
        )

    @api.onchange('visit_type')
    def _store_the_relative_value(self):
        if self.visit_type:
            self.appointment_mode = self.visit_type_id.appointment_mode
