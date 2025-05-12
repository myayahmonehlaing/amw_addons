from odoo import models, fields

DAYS = [
    ('0', 'Monday'),
    ('1', 'Tuesday'),
    ('2', 'Wednesday'),
    ('3', 'Thursday'),
    ('4', 'Friday'),
    ('5', 'Saturday'),
    ('6', 'Sunday'),
]


class HealthcareScheduleRulesLine(models.Model):
    _name = 'healthcare.schedule.rules.line'
    _description = "The healthcare schedule rule line list for the healthcare center"

    # === FIELDS ===#
    day_allowed = fields.Selection(selection=DAYS, string="Day Allowed",required=True)
    hour_from = fields.Float(string='Hour from')
    hour_to = fields.Float(string='Hour to')
    number_of_appointment_per_day=fields.Integer(string="Number of appointments per day")
    rule_id=fields.Many2one("healthcare.schedule.rules",string="Schedule Rules")

    # ===== SQL Constraint =====#

    # ===== method =======#
