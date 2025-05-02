from contextlib import nullcontext

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    payment_journal_id = fields.Many2one(
        'account.journal',
        string="Account Journal",
        check_company=True,
        store=True,
        groups="base.group_user",
        help="Select a journal."
    )

    def automate_validate_order(self):
        for order in self:
            # need to make the payment selection before the automate process of work
            if not order.payment_journal_id:
                raise ValidationError("Please select a payment journal before confirming the order.")

            # Check for each product that are avaliable
            for line in order.order_line:
                product = line.product_id
                require_qty = line.product_uom_qty
                # Get the available stock by checking the stock.quant model
                available_qty = self.env['stock.quant'].search([
                    ('product_id', '=', product.id),
                    ('location_id', '=', self.env.ref('stock.stock_location_stock').id)
                ]).quantity

                if available_qty < require_qty:
                    raise ValidationError((
                        f"Not enough stock for {product.display_name}. at {self.env.ref('stock.stock_location_stock').display_name}     "
                        f"Required: {require_qty}, Available: {available_qty}."
                    ))
            if order.state in ['draft', 'sent']:
                # Confirm the sale order if sate is draft
                super(SaleOrder, order).action_confirm()

            has_draft_invoices = bool(order.invoice_ids.filtered(lambda x: x.state == 'draft'))
            has_posted_invoices = bool(order.invoice_ids.filtered(lambda x: x.state == 'posted'))

            # to invoice
            # Create the invoice automatically # then invoiced
            if not has_draft_invoices and not has_posted_invoices:
                invoice = order._create_invoices()
                invoice.action_post()

            # Case 2: Draft invoices exist - Post them
            if has_draft_invoices and not has_posted_invoices:
                for draft_invoice in order.invoice_ids.filtered(lambda x: x.state == 'draft'):
                    draft_invoice.action_post()

            if order.invoice_status == 'invoiced':
                # Ensure payment journal is set
                journal = order.payment_journal_id

                # Register payment for the posted invoice
                for invoice in order.invoice_ids.filtered(lambda x: x.state == 'posted'):
                    if invoice.payment_state!='paid':
                        self._register_payment(order, invoice, journal)
                    else:
                        return True
        return True

    def _register_payment(self, order, invoice, journal):
        """Register payment for a given invoice."""
        payment_method = self.env.ref('account.account_payment_method_manual_in')  # Adjust as needed
        payment_vals = {
            'payment_type': 'inbound',
            'payment_method_id': payment_method.id,
            'partner_type': 'customer',
            'partner_id': order.partner_id.id,
            'amount': invoice.amount_total,
            'currency_id': invoice.currency_id.id,
            'journal_id': journal.id,
        }

        payment = self.env['account.payment'].create(payment_vals)
        payment.action_post()

        # Reconcile payment with the invoice
        payment_lines = self.env['account.move.line'].search([
            ('move_id', '=', payment.move_id.id),
            ('account_id', '=', order.partner_id.property_account_receivable_id.id)
        ])

        invoice_lines = self.env['account.move.line'].search([
            ('move_id', '=', invoice.id),
            ('account_id', '=', order.partner_id.property_account_receivable_id.id)
        ])

        # Perform reconciliation
        (payment_lines | invoice_lines).reconcile()
