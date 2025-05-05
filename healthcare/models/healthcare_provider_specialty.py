from odoo import models, fields

class HealthcareProvidersSpecialty(models.Model):
    _name = 'healthcare.providers.specialty'
    _description = "The provider list for the healthcare center"

    name = fields.Char(string="Name",store=True,required=True)