from odoo import models, fields

APPOINTMENT_MODE = [
    ('in_person', 'In Person'),
    ('phone_call', 'Phone Call'),
    ('video_consult', 'Video Consult')
]


class HealthcareVisitTypes(models.Model):
    _name = 'healthcare.visit.types'
    _description = "The visit type list for the healthcare center"
    _order='name'

    # === FIELDS ===#
    name = fields.Char(string="Name",
                       store=True,
                       required=True)
    appointment_mode = fields.Selection(selection=APPOINTMENT_MODE, string="Appointment Mode",required=True)
    charge = fields.Float(string="Charge",default="0.0",required=True)
    color = fields.Char(string="Color",required=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)


    # ===== SQL Constraint =====#

    # ===== method =======#
