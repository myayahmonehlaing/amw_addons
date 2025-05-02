from odoo import models, fields

DAYS = [
    ('Sun', 'Sunday'),
    ('Mon', 'Monday'),
    ('Tue', 'Tuesday'),
    ('Wed', 'Wednesday'),
    ('Thu', 'Thursday'),
    ('Fri', 'Friday'),
    ('Sat', 'Saturday')
]

TIME_DURATION=[
    ('12:00_pm',"12:00 PM"),
    ('12:30_pm',"12:30 PM"),
    ('1:00_pm',"1:00 PM"),
    ('1:30_pm',"1:30 PM"),
    ('2:00_pm',"2:00 PM"),
    ('2:30_pm',"2:30 PM"),
    ('3:00_pm',"3:00 PM"),
    ('3:30_pm',"3:30 PM"),
    ('4:00_pm',"4:00 PM"),
    ('4:30_pm',"4:30 PM"),
    ('5:00_pm',"5:00 PM"),
    ('5:30_pm',"5:30 PM"),
    ('6:00_pm',"6:00 PM"),
    ('6:30_pm',"6:30 PM"),
    ('7:00_pm',"7:00 PM"),
    ('7:30_pm',"7:30 PM"),
    ('8:00_pm',"8:00 PM"),
    ('8:30_pm',"8:30 PM"),
    ('9:00_pm',"9:00 PM"),
    ('9:30_pm',"9:30 PM"),
    ('10:00_pm',"10:00 PM"),
    ('10:30_pm',"10:30 PM"),
    ('11:00_pm',"11:00 PM"),
    ('11:30_pm',"11:30 PM"),
    ('12:00_pm',"12:00 PM"),
    ('12:30_pm',"12:30 PM"),

]

class HealthcareScheduleRulesLine(models.Model):
    _name = 'healthcare.schedule.rules.line'
    _description = "The healthcare schedule rule line list for the healthcare center"

    # === FIELDS ===#
    day_allowed = fields.Selection(selection=DAYS, string="Day Allowed",required=True)
    duration_from = fields.Selection(string="From",selection=TIME_DURATION)
    duration_to = fields.Selection(string="To",selection=TIME_DURATION)
    number_of_appointment_per_day=fields.Integer(string="Number of appointments per day")
    scheduled_rule=fields.Many2one("healthcare.schedule.rules",string="Schedule Rules")

    # ===== SQL Constraint =====#

    # ===== method =======#
