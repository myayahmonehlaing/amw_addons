from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

APPOINTMENT_GENDER = [
    ('male', "Male"),
    ('female', "Female")
]

APPOINTMENT_STATE = [
    ('draft', "Draft"),
    ('confirm', "Confirm")
]


class HealthcareBilling(models.Model):
    _name = 'healthcare.billing'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'analytic.mixin']
    _description = "The billing list for the healthcare center"

    # === FIELDS ===#
    name = fields.Char(string="Name", copy=False, default=lambda self: self._compute_name(),
                       store=True,
                       readonly=True)  # need to add compute #B00001
    appointment = fields.Many2one("healthcare.appointment", string="Appointment",required=True, tracking=True, )
    patient = fields.Many2one("healthcare.appointment.patients", string="Patient",required=True, tracking=True, )
    age = fields.Char(string="Age", related='patient.age', readonly=True, tracking=True, )
    sex = fields.Selection(selection=APPOINTMENT_GENDER, related='patient.gender', string="SEX", tracking=True, )
    facility = fields.Many2one("healthcare.facility", string="Facility",required=True, tracking=True, )
    provider = fields.Many2one("healthcare.providers", string="Provider",required=True, tracking=True, )
    date = fields.Date(string="Date", tracking=True, default=fields.Date.today,required=True)
    procedure = fields.One2many("healthcare.billing.procedures", "billing", string="Procedure",required=True, tracking=True)
    procedure_total = fields.Monetary(string="Procedure Total", compute="_compute_procedure_total",
                                      currency_field="currency")
    product = fields.One2many("healthcare.billing.products", "billing", string="Product", required=True, tracking=True)
    product_total = fields.Monetary(string="Product Total", compute="_compute_product_total", currency_field="currency")
    total_amount = fields.Monetary(string="Total Amount", compute="_compute_total_amount", currency_field="currency")
    amount_due = fields.Monetary(string="Amount Due", compute="_compute_amount_due", currency_field="currency")
    state = fields.Selection(selection=APPOINTMENT_STATE, string="State", store=True, tracking=True, default='draft')
    currency = fields.Many2one("res.currency", string="Currency", default=lambda self: self.env.company.currency_id,
                               tracking=True, )

    # sale_oder_id = fields.Char(string="Sale Order")
    # sale_order_count = fields.Integer(string="sale order count", compute="_get_sale_order")

    # ===== SQL Constraint =====#

    # ===== method =======#
    @api.model
    def _compute_name(self):

        # Search for the last billing name in the database
        last_billing = self.env['healthcare.billing'].search([], order='name desc', limit=1)
        if last_billing and last_billing.name:
            # Extract the numeric part and increment it
            last_number = int(last_billing.name[1:])  # Assumes format Bxxxxx
            new_number = last_number + 1
        else:
            # Start from 1 if no records exist
            new_number = 1

        # Format the new billing number as Bxxxxx
        return f"B{str(new_number).zfill(5)}"

    @api.onchange('appointment')
    def _store_the_relative_value(self):
        if self.appointment:
            # Fetch the related patient, facility, and provider from the appointment
            self.patient = self.appointment.patient
            self.facility = self.appointment.facility
            self.provider = self.appointment.provider


    @api.depends('procedure')
    def _compute_procedure_total(self):
        total = 0.0
        for procedure_list in self.procedure:
            total += procedure_list.amount
        self.procedure_total = total

    @api.depends('product')
    def _compute_product_total(self):
        total = 0
        for product_list in self.product:
            total += product_list.amount
        self.product_total = total

    @api.depends("product_total", "procedure_total")
    def _compute_total_amount(self):
        self.total_amount = self.product_total + self.procedure_total

    def _compute_amount_due(self):
        self.amount_due = self.product_total + self.procedure_total

    def create_sale_order(self):
        self.ensure_one()  # Ensure only one billing record is used

        order_lines = []
        order_lines.append((0, 0, {
            'display_type': 'line_section',
            'name': 'Procedures',
        }))
        # Add procedure lines
        for proc in self.procedure:
            if proc.description:
                order_lines.append((0, 0, {
                    'product_id': proc.description.id,
                    'product_uom_qty': proc.qty,
                    'price_unit': proc.price,
                }))
        order_lines.append((0, 0, {
            'display_type': 'line_section',
            'name': 'Products',
        }))
        # Add product lines
        for prod in self.product:
            if prod.product:
                order_lines.append((0, 0, {
                    'product_id': prod.product.id,
                    'product_uom_qty': prod.qty,
                    'price_unit': prod.price,
                }))

        # Create Sale Order
        sale_order = self.env['sale.order'].create({
            'partner_id': self.patient.partner.id,
            'date_order': fields.Date.today(),
            'warehouse_id': self.facility.warehouse.id,
            'order_line': order_lines,
        })

        # Store the created sale order to this form to use .
        # self.sale_oder_id=sale_order.id
        # self.sale_order_count=1

        # Confirm the sale order (equivalent to clicking "Confirm")
        sale_order.action_confirm()
        self.amount_due=self.total_amount

        if self.is_invoice_and_payment_enabled():
            # Create the invoice
            invoice = sale_order._create_invoices()
            invoice.action_post()  # Validate the invoice
            # Register payment for the invoice
            payment_method = self.env.ref('account.account_payment_method_manual_in')  # Adjust payment method if needed
            # journal = sale_order.payment_journal_id  # Use the first available bank journal
            journal = self.env['account.journal'].search([('type', '=', 'bank')], limit=1)
            if not journal:
                raise ValidationError("No bank journal found to register the payment.")

            # Create payment
            payment_vals = {
                'payment_type': 'inbound',
                'payment_method_id': payment_method.id,
                'partner_type': 'customer',
                'partner_id': sale_order.partner_id.id,
                'amount': invoice.amount_total,
                'currency_id': invoice.currency_id.id,
                'journal_id': journal.id,
                'invoice_ids': [(4, invoice.id)],
            }

            payment = self.env['account.payment'].create(payment_vals)
            payment.action_post()  # Post the payment to mark it as paid
            # Need to change state to paid

            # Reconcile the payment with the invoice to mark it as paid
            payment_lines = self.env['account.move.line'].search([
                ('move_id', '=', payment.move_id.id),
                ('account_id', '=', sale_order.partner_id.property_account_receivable_id.id)
            ])

            invoice_lines = self.env['account.move.line'].search([
                ('move_id', '=', invoice.id),
                ('account_id', '=', sale_order.partner_id.property_account_receivable_id.id)
            ])

            # Reconcile the lines
            payment_lines |= invoice_lines
            payment_lines.reconcile()

            if payment.state != 'paid':
                payment.action_validate()  # validate in payment
            self.amount_due = invoice.amount_residual

        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'target': 'current',
        }

    def is_invoice_and_payment_enabled(self):
        val=self.env['ir.config_parameter'].sudo().get_param('charm_ehr.invoice_and_payment')
        return val
