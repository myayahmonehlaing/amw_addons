from odoo import models, fields, api

class HealthcareImages(models.Model):
    _name = 'healthcare.image.images'
    _description = "The multiple images list for the healthcare center"

    # === FIELDS ===#
    image=fields.Image(string="Image")
    image_relation_id=fields.Many2one("healthcare.images",string="Image Relation")

    # ===== SQL Constraint =====#

    #===== method =======#

