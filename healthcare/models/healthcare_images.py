from odoo import models, fields, api


class HealthcareImages(models.Model):
    _name = 'healthcare.images'
    _description = "The images list for the healthcare center"

    # === FIELDS ===#
    name = fields.Char( string="Name",copy=False, default=lambda self: self._compute_name(),
                       store=True,
                       readonly=True) #need to add compute #IM00001
    patient_id=fields.Many2one("healthcare.patients",string="Patient",required=True)
    provider_id=fields.Many2one("healthcare.providers",string="Provider",required=True)
    date=fields.Date(string="Date",default=fields.Date.today,required=True)
    images=fields.One2many("healthcare.image.images","image_relation",string="Images",copy=False)


    # ===== SQL Constraint =====#

    #===== method =======#
    @api.model
    def _compute_name(self):
        # Search for the last image name in the database
        last_image = self.env["healthcare.images"].search([], order='name desc', limit=1)
        if last_image and last_image.name:
            # Extract the numeric part and increment it
            last_number = int(last_image.name[2:])  # Assumes format IMxxxxx
            new_number = last_number + 1
        else:
            # Start from 1 if no records exist
            new_number = 1

        # Format the new image number as IMxxxxx
        return f"IM{str(new_number).zfill(5)}"


