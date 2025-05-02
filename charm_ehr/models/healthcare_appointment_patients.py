"""
Work for patient list
"""
from odoo import models, fields, api, _
from odoo.exceptions import UserError

GENDER_TYPE = [
    ("female", "Female"),
    ("male", "Male"),
]
class HealthcareAppointmentPatients(models.Model):
    """
    Handle patient information
    """
    _name = "healthcare.appointment.patients"
    _inherit = ["mail.thread", "mail.activity.mixin", "analytic.mixin"]
    _description = "The appointment patients list for the healthcare center"

    # === FIELDS ===#
    name = fields.Char(
        string="Name",
        required=True,
        tracking=True,
    )
    patient_id = fields.Char(
        string="ID",
        copy=False,
        default=lambda self: self.compute_id(),
        store=True,
        required=True,
        readonly=True,
    )  # need to add compute for PAT00001
    partner = fields.Many2one(
        "res.partner", string="Partner", required=True, tracking=True
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
    email = fields.Char(
        string="Email",
        required=True,
        tracking=True,
    )
    phone = fields.Char(
        string="Phone",
        required=True,
        tracking=True,
    )

    # Address fields
    street = fields.Char("Street", readonly=False, store=True)
    street2 = fields.Char("Street2", readonly=False, store=True)
    zip = fields.Char("Zip", change_default=True, readonly=False, store=True)
    city = fields.Char("City", readonly=False, store=True)
    state_id = fields.Many2one(
        "res.country.state",
        string="State",
        readonly=False,
        store=True,
        domain="[('country_id', '=?', country_id)]",
    )
    country_id = fields.Many2one(
        "res.country", string="Country", readonly=False, store=True
    )

    # ===== SQL Constraint =====#

    # ===== method =======#
    # To compute the sequence value of PAT000001
    @api.model
    def compute_id(self):
        """
        Search for the last patient id in the database
        """
        last_patient_id = self.env["healthcare.appointment.patients"].search(
            [], order="patient_id desc", limit=1
        )
        if last_patient_id and last_patient_id.patient_id:
            # Extract the numeric part and increment it
            last_number = int(last_patient_id.patient_id[3:])  # Assumes format PATxxxxx
            new_number = last_number + 1
        else:
            # Start from 1 if no records exist
            new_number = 1

        # Format the new patient id as PATxxxxx
        return f"PAT{str(new_number).zfill(5)}"

    # compute the age based on dob, if age is -value:raise error and other age can accept to store
    @api.depends("dob")
    def _compute_age(self):
        for record in self:
            if record.dob:
                today = fields.Date.today()
                date_diff = today - record.dob

                years = date_diff.days // 365
                if years > 0:
                    record.age = str(years) + "year"
                elif years == 0:
                    record.age = "0 year"
                else:
                    raise UserError(_("Please select the correct birthday date!"))

            else:
                record.age = ""

    # When partner is selected from res.partner, assign the value to the fields
    @api.onchange("partner")
    def _onchange_partner(self):
        for rec in self:
            if rec.partner:
                rec.name = rec.partner.name
                rec.gender = (
                    rec.partner.gender if hasattr(rec.partner, "gender") else False
                )
                rec.dob = (
                    rec.partner.birthday if hasattr(rec.partner, "birthday") else False
                )
                rec.email = rec.partner.email
                rec.phone = rec.partner.phone
                rec.street = rec.partner.street
                rec.street2 = rec.partner.street2
                rec.zip = rec.partner.zip
                rec.city = rec.partner.city
                rec.state_id = rec.partner.state_id
                rec.country_id = rec.partner.country_id

    # To display name: mgmg/m/21years when this model is used for Many2one field type
    @api.depends_context("company")
    @api.depends("name", "age", "gender")
    def _compute_display_name(self):
        for appointment_patient in self:
            gender_short = (
                "m"
                if appointment_patient.gender == "male"
                else "f" if appointment_patient.gender == "female" else ""
            )
            appointment_patient.display_name = (
                f"{appointment_patient.name} / {gender_short} / "
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
                "m" if rec.gender == "male" else "f" if rec.gender == "female" else ""
            )
            name = f"{rec.name} / {gender_short} / {rec.age}years"
            result.append((rec.id, name))
        return result
