"""
Work for Appointment Status list for check the state of the appointment
"""

from odoo import api, fields, models, tools, _

STATUS_SELECTION = [
    ('in-progress', 'Running'),
    ('close', 'Closed'),
  ]

class HealthcareAppointmentStatus(models.Model):
    """
    Handle for the status of appointments
    """
    _name = "healthcare.appointment.date"
    _description = " Appointment Date"

    name = fields.Char(string="Name",  default=lambda self: self._compute_name(),)  # check in, confirm ...
    date = fields.Date(string="Date")
    date_from = fields.Datetime(string="Date From ")
    date_to = fields.Datetime(string="Date To")
    provider_id = fields.Many2one("healthcare.providers","Provider")
    resource_id = fields.Many2one(
        "healthcare.resources", string="Resource", tracking=True
    )
    specialty_id = fields.Many2one("healthcare.providers.speciality", string="Specialty", related='provider_id.speciality_id')
    facility_id = fields.Many2one("healthcare.facility", string="Facility", required=True)
    color = fields.Char(related='specialty_id.color')
    status = fields.Selection(STATUS_SELECTION)
    appointment_ids = fields.One2many("healthcare.appointment","type_id", string="Appointments")
    appointment_count = fields.Integer("Appointment Count",compute='_compute_appointment_ids')

    @api.depends('appointment_ids')
    def _compute_appointment_ids(self):
        for record in self:
            record.appointment_count = len(record.appointment_ids)

    def action_generate_appointment_date(self):
        context = {}
        return {
            "res_model": "healthcare.generate.date",
            "views": [[False, "form"]],
            "target": "new",
            "type": "ir.actions.act_window",
            "context": context,
        }

    def action_create_appointment(self):
        self.ensure_one()
        # If category uses sequence, set next sequence as name
        # (if not, set category name as default name).
        return {
            "type": "ir.actions.act_window",
            "res_model": "healthcare.appointment",
            "views": [[False, "form"]],
            "context": {
                # 'default_name': _('New') if self.automated_sequence else self.name,
                'default_type_id': self.id,
                'default_provider_id': self.provider_id.id,
                'default_date': self.date
            },
        }

    def action_view_appointment(self):
        print("...........................")

