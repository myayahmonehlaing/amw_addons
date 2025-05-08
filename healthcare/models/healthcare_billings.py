from odoo import models, fields, api, _
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
    _order = 'name desc'

    # === FIELDS ===#
    name = fields.Char(string="Name", copy=False, default="/",
                       store=True,
                       readonly=True)  # need to add compute #B00001
    appointment_id = fields.Many2one("healthcare.appointment", string="Appointment", required=True, tracking=True, )
    patient_id = fields.Many2one("healthcare.patients", string="Patient", required=True, tracking=True, )
    age = fields.Char(string="Age", related='patient_id.age', readonly=True, tracking=True, )
    sex = fields.Selection(selection=APPOINTMENT_GENDER, related='patient_id.gender', string="Sex", tracking=True, )
    facility_id = fields.Many2one("healthcare.facility", string="Facility", required=True, tracking=True, )
    provider_id = fields.Many2one("healthcare.providers", string="Provider", required=True, tracking=True, )
    date = fields.Date(string="Date", tracking=True, default=fields.Date.today, required=True)
    procedure_line_ids = fields.One2many("healthcare.billing.procedures", "billing_id", string="Procedure",
                                         required=True, )
    procedure_total = fields.Monetary(string="Procedure Total", compute="_compute_procedure_total",
                                      currency_field="currency_id")
    product_line_ids = fields.One2many("healthcare.billing.products", "billing_id", string="Product", required=True)
    product_total = fields.Monetary(string="Product Total", compute="_compute_product_total",
                                    currency_field="currency_id")
    total_amount = fields.Monetary(string="Total Amount", compute="_compute_total_amount", currency_field="currency_id",
                                   tracking=True)
    amount_due = fields.Monetary(string="Amount Due", compute="_compute_amount_due", currency_field="currency_id")
    state = fields.Selection(selection=APPOINTMENT_STATE, string="State", store=True, tracking=True, default='draft')
    currency_id = fields.Many2one("res.currency", string="Currency", default=lambda self: self.env.company.currency_id,
                                  tracking=True, )
    sale_order_count = fields.Integer(string="sale order count", compute="_get_sale_order")
    invoice_count = fields.Integer(string="invoice count", compute="_get_invoice")
    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)

    # ===== SQL Constraint =====#

    # ===== method =======#

    @api.onchange('appointment_id')
    def _store_the_relative_value(self):
        if self.appointment_id:
            # Fetch the related patient, facility, and provider from the appointment
            self.patient_id = self.appointment_id.patient_id
            self.facility_id = self.appointment_id.facility_id
            self.provider_id = self.appointment_id.provider_id

    @api.depends('procedure_line_ids')
    def _compute_procedure_total(self):
        total = 0.0
        for procedure_list in self.procedure_line_ids:
            total += procedure_list.amount
        self.procedure_total = total

    @api.depends('product_line_ids')
    def _compute_product_total(self):
        total = 0
        for product_list in self.product_line_ids:
            total += product_list.amount
        self.product_total = total

    @api.depends("product_total", "procedure_total")
    def _compute_total_amount(self):
        self.total_amount = self.product_total + self.procedure_total

    def _compute_amount_due(self):
        invoice = self.env['account.move'].search([
            ('bill_ids.name', '=', self.name),  # Use 'bill_ids.name' to link with bill name
        ])
        if(invoice):
            self.amount_due = invoice.amount_residual



    def create_sale_order(self):
        self.ensure_one()  # Ensure only one billing record is used

        self.state = 'confirm'
        if self.name == '/':
            self.name = self.env['ir.sequence'].next_by_code('healthcare.billing.code') or '/'

        order_lines = []
        order_lines.append((0, 0, {
            'display_type': 'line_section',
            'name': 'Procedures',
        }))
        # Add procedure lines
        for proc in self.procedure_line_ids:
            if proc.product_id:
                order_lines.append((0, 0, {
                    'product_id': proc.product_id.id,
                    'product_uom_qty': proc.qty,
                    'price_unit': proc.unit_price,
                }))
        order_lines.append((0, 0, {
            'display_type': 'line_section',
            'name': 'Products',
        }))
        # Add product lines
        for prod in self.product_line_ids:
            if prod.product_id:
                order_lines.append((0, 0, {
                    'product_id': prod.product_id.id,
                    'product_uom_qty': prod.qty,
                    'price_unit': prod.unit_price,
                }))

        # Create Sale Order
        sale_order = self.env['sale.order'].create({
            'partner_id': self.patient_id.partner_id.id,
            'date_order': fields.Date.today(),
            'warehouse_id': self.facility_id.warehouse_id.id,
            'order_line': order_lines,
            'bill_ids': self.id,
        })

        # Store the created sale order to this form to use .
        # self.sale_oder_id=sale_order.id
        # self.sale_order_count=1

        # Confirm the sale order (equivalent to clicking "Confirm")
        sale_order.action_confirm()
        self.amount_due = self.total_amount

        if self.is_invoice_and_payment_enabled():
            # Create the invoice
            invoice = sale_order._create_invoices()
            invoice.action_post()  # Validate the invoice
            # For set the value after invoice //Here if after partial payment is do the value is not refresh.
            self.amount_due = invoice.amount_residual

    def is_invoice_and_payment_enabled(self):
        val = self.env['ir.config_parameter'].sudo().get_param('charm_ehr.invoice_and_payment')
        return val

    # To get the count of sale order
    @api.depends('name')
    def _get_sale_order(self):
        """
        This method calculates the count of open sale orders for the given billing name.
        """
        for billing in self:
            # Search for sale orders linked to the current billing based on 'bill name'
            open_orders = self.env['sale.order'].search([
                ('bill_ids.name', '=', billing.name),  # Use 'bill_ids.name' to link with bill name
                ('state', '=', 'sale')
            ])
            invoice = self.env['account.move'].search([
                ('bill_ids.name', '=', billing.name),  # Use 'bill_ids.name' to link with bill name
            ])

            billing.sale_order_count = len(open_orders)
            billing.invoice_count = len(invoice)

    # To navigate to the relative sale order
    def action_view_saleorder(self):
        # Search for sale orders linked to the current billing based on 'bill name'
        sale_order = self.env['sale.order'].search([
            ('bill_ids.name', '=', self.name),  # Use 'bill_ids.name' to link with bill name
            ('state', '=', 'sale')
        ])

        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'target': 'current',
        }


    # To navigate to the relative invoice
    def action_view_invoice(self):
        # Search for invoice linked to the billing based on 'bill name'
        invoice = self.env['account.move'].search([
            ('bill_ids.name', '=', self.name),  # Use 'bill_ids.name' to link with bill name
        ])

        return {
            'type': 'ir.actions.act_window',
            'name': 'Account Move',
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'target': 'current',
        }
