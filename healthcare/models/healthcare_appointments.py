from odoo import models, fields, api, _


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
    _order = "name desc"

    # === FIELDS ===#
    name = fields.Char(
        string="Name",
        copy=False,
        default=lambda self: _("New"),
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
    status_id = fields.Many2one(
        "healthcare.appointment.status",
        string="Status",
        default=lambda self: self.get_default_status(),
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
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)
    # ===== SQL Constraint =====#

    # ===== method =======#
    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("healthcare.appointment.code")
                or "New"
            )
        return super().create(vals)

    @api.model
    def get_default_status(self):
        return self.env["healthcare.appointment.status"].search(
            [("default", "=", True)], limit=1
        )

    @api.onchange("visit_type_id")
    def _store_the_relative_value(self):
        if self.visit_type_id:
            self.appointment_mode = self.visit_type_id.appointment_mode
