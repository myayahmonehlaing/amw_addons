from odoo import models, fields

class HealthcareProvidersSpeciality(models.Model):
    _name = 'healthcare.providers.speciality'
    _description = "The provider list for the healthcare center"

    name = fields.Char(string="Name",store=True,required=True)