"""
Work for patient list
"""
from odoo import models, fields, api, _
from odoo.exceptions import UserError

GENDER_TYPE = [
    ("female", "Female"),
    ("male", "Male"),
]
class HealthcarePatients(models.Model):
    """
    Handle patient information
    """
    _name = "healthcare.patients"
    _inherits = {'res.partner': 'partner_id'}
    _inherit = ["mail.thread", "mail.activity.mixin", "analytic.mixin"]
    _description = "Patients"
    _order = 'name'

    # === FIELDS ===#

    number = fields.Char(
        string="ID",
        copy=False,
        default=lambda self: _('New'),
        store=True,
        required=True,
        readonly=True,
    )  # need to add compute for PAT00001
    partner_id = fields.Many2one(
        "res.partner", string="Partner",auto_join=True, index=True, ondelete="cascade", required=True
    )
    gender = fields.Selection(
        selection=GENDER_TYPE,
        string="Gender",
        tracking=True,
    )
    dob = fields.Date(
        string="DOB",
        tracking=True,
    )  # Hr.employee can get this fields
    age = fields.Char(
        string="Age", compute="_compute_age", readonly=True, store=True
    )  # need to add compute



    # ===== method =======#
    # To compute the sequence value of PAT000001
    @api.model
    def create(self, vals):
        if vals.get('number', 'New') == 'New':
            vals['number'] = self.env['ir.sequence'].next_by_code('healthcare.patients.code') or 'New'
        return super(HealthcarePatients, self).create(vals)


    # compute the age based on dob, if age is -value:raise error and other age can accept to store
    @api.depends("dob")
    def _compute_age(self):
        for record in self:
            if record.dob:
                today = fields.Date.today()
                date_diff = today - record.dob

                years = date_diff.days // 365
                if years > 0:
                    record.age = str(years) + " Years"
                elif years == 0:
                    record.age = "0 Years"
                else:
                    raise UserError(_("Please select the correct birthday date!"))

            else:
                record.age = ""

    # When partner is selected from res.partner, assign the value to the fields


    # To display name: mgmg/m/21years when this model is used for Many2one field type
    @api.depends_context("company")
    @api.depends("name", "age", "gender")
    def _compute_display_name(self):
        for appointment_patient in self:
            gender_short = (
                "M"
                if appointment_patient.gender == "male"
                else "F" if appointment_patient.gender == "female" else ""
            )
            appointment_patient.display_name = (
                f"{appointment_patient.name} - {gender_short} / "
                f"{appointment_patient.age}"
            )

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """
        Here need to add for the search by age or gender. in my case, it can only search by name.
        """
        args = args or []
        domain = []
        if name:
            domain = [
                "|",
                "|",
                ("name", operator, name),
                ("gender", operator, name),
                ("age", operator, name),
            ]
        return self.search(domain + args, limit=limit).name_get()

    def name_get(self):
        """
        To reshow the search value of the patient
        """
        result = []
        for rec in self:
            gender_short = (
                "M" if rec.gender == "male" else "F" if rec.gender == "female" else ""
            )
            name = f"{rec.name} - {gender_short} / {rec.age}"
            result.append((rec.id, name))
        return result

