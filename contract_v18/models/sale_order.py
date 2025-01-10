from email.policy import default

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    disable_company_onchange = fields.Boolean(store=False,default=True)

    # Define the selection field for contracts
    contract_id = fields.Many2one('sale.contract',
                                  string="Sales Contract",
                                  domain=[('state', '=', 'contract')],
                                  help="Select a valid Sales Contract."
                                  )


    @api.onchange('contract_id')
    def _onchange_sale_contract(self):
        self.disable_company_onchange = True
        # Clear existing sale order lines
        self.order_line = False
        if self.contract_id:
            selected_contract = self.contract_id

            if selected_contract:
                # Set the customer (partner) from the contract
                self.partner_id = selected_contract.partner_id

            for contract_line in selected_contract.line_ids:
                product = contract_line.product_id
                if not product or contract_line.qty_to_sale <= 0:
                    continue

                # Prepare new sale order line values
                copied_vals = {
                    'order_id': self.id,  # Link to current sale order
                    'product_id': product.id,  # Product from contract line
                    'product_uom': product.uom_id.id,  # Default unit of measure
                    'product_uom_qty': contract_line.qty_to_sale,  # Quantity from contract line
                    'price_unit': contract_line.unit_price,  # Unit price from contract line
                    'name': product.display_name or '',  # Description of the product
                    'tax_id': [(6, 0, [])],  # Set default empty tax list
                    'discount': 0.0,  # Set default discount to 0
                }

                # Add the new line to the order lines
                self.order_line += self.env['sale.order.line'].new(copied_vals)

    @api.onchange('company_id')
    def _onchange_company_id_warning(self):
        # Skip warning if _disable_company_onchange is True
        if self.disable_company_onchange:
            return  # Do not trigger the warning
        # import pdb;pdb.set_trace()
        self.show_update_pricelist = True
        if self.order_line and self.state == 'draft':
            return {
                'warning': {
                    'title': _("Warning for the change of your quotation's company"),
                    'message': _("Changing the company of an existing quotation might need some "
                                 "manual adjustments in the details of the lines. You might "
                                 "consider updating the prices."),
                }
            }
        self.disable_company_onchange=False
