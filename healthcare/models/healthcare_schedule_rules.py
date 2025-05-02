from odoo import models, fields,api

class HealthcareScheduleRules(models.Model):
    _name = 'healthcare.schedule.rules'
    _description = "The healthcare schedule rule list for the healthcare center"

    # === FIELDS ===#
    name=fields.Char(string="Name",compute="_compute_name")
    facility = fields.Many2one("healthcare.facility", string="Facility",required=True)
    provider = fields.Many2one("healthcare.providers", string="Provider",required=True)
    visit_types = fields.Many2one("healthcare.visit.types", string="Visit Types",required=True)
    scheduled_rules_line = fields.One2many("healthcare.schedule.rules.line","scheduled_rule", string="Scheduled Rules Lines")
    # ===== SQL Constraint =====#

    # ===== method =======#
    @api.depends("provider", "facility")
    def _compute_name(self):
        for record in self:
            facility_name = record.facility.name if record.facility else ''
            provider_name = record.provider.name if record.provider else ''
            record.name = f"{provider_name} - {facility_name}"

