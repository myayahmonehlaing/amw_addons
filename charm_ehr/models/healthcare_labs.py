from odoo import models, fields, api


class HealthcareLabs(models.Model):
    _name = 'healthcare.labs'
    _description = "The labs list for the healthcare center"

    # === FIELDS ===#
    name = fields.Char( string="Name",copy=False, default=lambda self: self._compute_name(),
                       store=True,
                       readonly=True) #need to add compute #LB00001
    patient=fields.Many2one("healthcare.appointment.patients",string="Patient",required=True)
    provider=fields.Many2one("healthcare.providers",string="Provider",required=True)
    date=fields.Date(string="Date",required=True)
    results=fields.Text(string="Results",copy=True)
    diagnosis=fields.Text(string="Diagnosis",copy=True)


    # ===== SQL Constraint =====#

    #===== method =======#
    @api.model
    def _compute_name(self):

        # Search for the last lab name in the database
        last_lab = self.env["healthcare.labs"].search([], order='name desc', limit=1)
        if last_lab and last_lab.name:
            # Extract the numeric part and increment it
            last_number = int(last_lab.name[2:])  # Assumes format LBxxxxx
            new_number = last_number + 1
        else:
            # Start from 1 if no records exist
            new_number = 1

        # Format the new lab number as LBxxxxx
        return f"Lb{str(new_number).zfill(5)}"


