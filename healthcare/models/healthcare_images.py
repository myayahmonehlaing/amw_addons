from odoo import models, fields, api,_


class HealthcareImages(models.Model):
    _name = 'healthcare.images'
    _description = "The images list for the healthcare center"
    _order = 'name desc'

    # === FIELDS ===#
    name = fields.Char( string="Name",copy=False, default=lambda self: _('New'),
                       store=True,
                       readonly=True) #need to add compute #IM00001
    patient_id=fields.Many2one("healthcare.patients",string="Patient",required=True)
    provider_id=fields.Many2one("healthcare.providers",string="Provider",required=True)
    date=fields.Date(string="Date",default=fields.Date.today,required=True)
    images_ids=fields.One2many("healthcare.image.images","image_relation_id",string="Images",copy=False)
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)


    # ===== SQL Constraint =====#

    #===== method =======#
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('healthcare.images.code') or 'New'
        return super(HealthcareImages, self).create(vals)


