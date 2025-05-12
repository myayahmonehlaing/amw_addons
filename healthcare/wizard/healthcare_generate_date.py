# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from datetime import date, datetime, timedelta



class HealthcareGenerateDate(models.TransientModel):
    _name = 'healthcare.generate.date'

    date_from = fields.Date(string="Date From", default=lambda self: date.today() )
    date_to = fields.Date(string="Date To", default=lambda self: date.today() + timedelta(days=30))
    provider_id = fields.Many2one("healthcare.providers", "Provider")

    def action_generate_date(self):
        domain = []
        if self.provider_id:
            domain = [('provider_id', '=', self.provider_id.id)]
        schedule_rules = self.env['healthcare.schedule.rules'].search(domain)

        current_date = self.date_from
        end_date = self.date_to
        healthcare_date = self.env['healthcare.appointment.date']

        def float_to_time_str(float_time):
            hours = int(float_time)
            minutes = int(round((float_time - hours) * 60))
            return f"{hours:02d}:{minutes:02d}"

        if schedule_rules:
            while current_date <= end_date:
                weekday = current_date.weekday()

                for rule in schedule_rules.scheduled_rules_line_ids:
                    if weekday == int(rule.day_allowed):
                        # existing_date = healthcare_date.search([('date','=',current_date),('provider_id', '=', self.provider_id)])
                        # if not existing_date:

                        healthcare_date.create({
                            'name':  f"{rule.rule_id.provider_id.name} - ( {current_date} {float_to_time_str(rule.hour_from)} - {float_to_time_str(rule.hour_to)} )",
                            'date': current_date,
                            'date_from':  datetime.combine(current_date, datetime.min.time()) + timedelta(hours=rule.hour_from) - timedelta(hours=6.5),
                            'date_to': datetime.combine(current_date, datetime.min.time()) + timedelta(hours=rule.hour_to) -  timedelta(hours=6.5),
                            'provider_id': rule.rule_id.provider_id.id,
                            'facility_id': rule.rule_id.facility_id.id,
                            'status':'in-progress'

                        })
                current_date += timedelta(days=1)
        else:
            print("No schedule rule")
