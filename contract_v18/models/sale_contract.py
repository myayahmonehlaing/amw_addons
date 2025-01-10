import json

from odoo import models, fields, api, _
from datetime import date

SALE_Contract_STATE = [
    ('draft', "Quotation"),
    ('contract', "Sale Contract"),
    ('closed', "Closed"),
]


class SaleContract(models.Model):
    _inherit = 'mail.thread'
    _name = 'sale.contract'
    _description = "Sales Contract"

    # === FIELDS ===#
    name = fields.Char(string="Contract Number", copy=False, default=lambda self: self._compute_contract_number(),
                       store=True,
                       readonly=True)

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Customer",
        required=True, change_default=True, index=True)

    user_id = fields.Many2one(
        comodel_name='res.users',
        string="Salesperson",
        compute='_compute_user_id',
        store=True, readonly=False, precompute=True, index=True,
        tracking=2,
        domain=lambda self: "[('groups_id', '=', {}), ('share', '=', False), ('company_ids', '=', company_id)]".format(
            self.env.ref("sales_team.group_sale_salesman").id
        ))

    date = fields.Date(string="Contract Date",
                       default=lambda self: date.today(), )

    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string="Pricelist",
        store=True, readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="If you change the pricelist, only newly added lines will be affected.")

    company_id = fields.Many2one(
        comodel_name='res.company',
        required=True, index=True,
        default=lambda self: self.env.company)

    line_ids = fields.One2many(
        comodel_name='sale.contract.line',
        inverse_name='contract_id',
        string="Contract Lines",
        copy=True, auto_join=True)

    total = fields.Float(string="Total", store=True, compute="_compute_total", )

    state = fields.Selection(
        selection=SALE_Contract_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=True,
        default='draft'
    )
    sale_order_count = fields.Integer(string="Sale Order", default=0, compute='_get_sale_order')

    @api.model
    def _compute_contract_number(self):

        # Search for the last contract name in the database
        last_contract = self.env['sale.contract'].search([], order='name desc', limit=1)
        if last_contract and last_contract.name:
            # Extract the numeric part and increment it
            last_number = int(last_contract.name[2:])  # Assumes format SCxxxxx
            new_number = last_number + 1
        else:
            # Start from 1 if no records exist
            new_number = 1

        # Format the new contract number as SCxxxxx
        return f"SC{str(new_number).zfill(5)}"

    @api.depends('partner_id')
    def _compute_user_id(self):
        for contract in self:
            if contract.partner_id and not (contract._origin.id and contract.user_id):
                # Recompute the salesman on partner change
                #   * if partner is set (is required anyway, so it will be set sooner or later)
                #   * if the order is not saved or has no salesman already
                contract.user_id = (
                        contract.partner_id.user_id
                        or contract.partner_id.commercial_partner_id.user_id
                        or (self.env.user.has_group('sales_team.group_sale_salesman') and self.env.user)
                )

    def action_confirm(self):
        self.state = 'contract'
        return True

    def action_close(self):
        self.state = 'closed'
        return True

    def action_draft(self):
        self.state = 'draft'
        return True

    # Call from sale contract line
    def _get_lang(self):

        if self.partner_id.lang and not self.partner_id.is_public:
            return self.partner_id.lang

        return self.env.lang

    def _get_thread_with_access(self, thread_id, **kwargs):
        # Placeholder logic
        return self.browse(thread_id)

    @api.depends('partner_id', 'company_id')
    def _compute_pricelist_id(self):

        for contract in self:
            if contract.state != 'draft':
                continue
            if not contract.partner_id:
                contract.pricelist_id = False
                continue
            contract = contract.with_company(contract.company_id)
            contract.pricelist_id = contract.partner_id.property_product_pricelist

    @api.depends('line_ids.subtotal')
    def _compute_total(self):
        for record in self:
            record.total = sum(line.subtotal for line in record.line_ids)

    # Update for '_get_sale_order' method
    @api.depends('name')
    def _get_sale_order(self):
        """
        This method calculates the count of open sale orders for the given contract.
        It considers sale orders whose state is neither 'closed' nor 'cancelled'.
        """
        for contract in self:
            # Search for sale orders linked to the current contract based on 'contract_id' (linked via contract name)
            open_orders = self.env['sale.order'].search([
                ('contract_id.name', '=', contract.name),  # Use 'contract_id.name' to link with contract name
                ('state', '=', 'sale')
            ])
            contract.sale_order_count = len(open_orders)
            # Loop through contract lines and update qty_to_sale
            for line in contract.line_ids:
                total_qty_invoiced = 0
                # Search for sale.order.lines related to the contract's line product
                sale_order_lines = self.env['sale.order.line'].search([
                    ('order_id.contract_id.name', '=', contract.name),  # Link by contract name
                    ('product_id', '=', line.product_id.id),  # Match product
                    ('state', '=', 'sale')  # Only open sale order lines
                ])

                # Sum up the qty_invoiced for the sale order lines of the product
                for order_line in sale_order_lines:
                    total_qty_invoiced += order_line.product_uom_qty

                # Update the qty_to_sale for the contract line
                line.sale_quantity = total_qty_invoiced

                line.qty_to_sale = line.quantity - line.sale_quantity

    def action_view_sale_order_for_contract(self):
        """
        Returns an action to display sale orders linked to this contract.
        """
        # Fetch open sale orders related to this contract
        sale_orders = self.env['sale.order'].search([('contract_id', '=', self.id)])

        # Initialize the action dictionary
        action = self.env.ref('sale.action_orders').read()[0]

        # Check the number of sale orders and configure the action accordingly
        if len(sale_orders) > 1:
            action['domain'] = [('id', 'in', sale_orders.ids)]
        elif len(sale_orders) == 1:
            form_view = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['views'] = form_view
            action['res_id'] = sale_orders.id
        else:
            return {'type': 'ir.actions.act_window_close'}

        # Set the context to include the contract ID
        action['context'] = {
            'default_contract_id': self.id,
        }
        return action

    @api.model
    def default_get(self, fields):
        res = super(SaleContract, self).default_get(fields)
        res['company_id'] = self.env.company.id
        return res

    def _get_contract_lines_to_report(self):
        def show_line(line):
            # Customize the conditions for displaying lines based on your fields
            if line.product_id and line.quantity > 0:  # Example condition
                return True
            return False

        return self.line_ids.filtered(show_line)

