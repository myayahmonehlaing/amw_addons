from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleReportWizard(models.TransientModel):
    _name = 'sale.report.wizard'
    _description = 'Sale Report Wizard'

    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)

    def action_generate_report(self):
        # Implement your logic to handle the dates and generate the report
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sales Report',
            'view_mode': 'tree',
            'res_model': 'sale.order',  # Replace with your target model
            'domain': [('date_order', '>=', self.date_from), ('date_order', '<=', self.date_to)],
        }

    def action_generate_pdf_report(self):
        if self.date_from > self.date_to:
            raise UserError("Start date cannot be after end date.")

        # Trigger the report action
        return self.env.ref('sale_report.action_report_saleorder_date_range').report_action(self)

    def get_sale_orders(self):
        """Fetch sale orders within the selected date range."""
        return self.env['sale.order'].search([
            ('date_order', '>=', self.date_from),
            ('date_order', '<=', self.date_to)
        ])

    def action_generate_xls_report(self):
        if self.date_from > self.date_to:
            raise UserError("Start date cannot be after end date.")

        # Redirect to the custom controller to generate and download the report
        return {
            'type': 'ir.actions.act_url',
            'url': '/download/sale_report_xls?date_from={}&date_to={}'.format(
                self.date_from, self.date_to
            ),
            'target': 'self',
        }
