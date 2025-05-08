from odoo import models, fields,api

class HealthcareScheduleRules(models.Model):
    _name = 'healthcare.schedule.rules'
    _description = "The healthcare schedule rule list for the healthcare center"
    _order='name'

    # === FIELDS ===#
    name=fields.Char(string="Name",compute="_compute_name" ,store=True)
    facility_id = fields.Many2one("healthcare.facility", string="Facility",required=True)
    provider_id = fields.Many2one("healthcare.providers", string="Provider",required=True)
    visit_type_id = fields.Many2one("healthcare.visit.types", string="Visit Types",required=True)
    scheduled_rules_line_ids = fields.One2many("healthcare.schedule.rules.line","rule_id", string="Scheduled Rules Lines")
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)
    # ===== SQL Constraint =====#

    # ===== method =======#
    @api.depends("provider_id", "facility_id")
    def _compute_name(self):
        for record in self:
            facility_name = record.facility_id.name if record.facility_id else ''
            provider_name = record.provider_id.name if record.provider_id else ''
            record.name = f"{provider_name} - {facility_name}"

