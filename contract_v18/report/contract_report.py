from odoo import api, fields, models

SALE_CONTRACT_STATE = [
    ('draft', "Quotation"),
    ('contract', "Sale Contract"),
    ('closed', "Closed"),
]

class ContractReport(models.Model):
    _name = "sale.contract.report"
    _description = "Sale Contract Analysis Report"
    _auto = False
    _rec_name = 'date'
    _order = 'date desc'

    # Sale contract fields
    name = fields.Char(string="Contract Number", readonly=True)
    partner_id = fields.Many2one(comodel_name='res.partner', string="Customer", readonly=True)
    user_id = fields.Many2one(comodel_name='res.users', string="Salesperson", readonly=True)
    date = fields.Date(string="Contract Date", readonly=True)
    company_id = fields.Many2one(comodel_name='res.company', string="Company", readonly=True)
    state = fields.Selection(selection=SALE_CONTRACT_STATE, string="Status", readonly=True)

    # Customer-related fields
    commercial_partner_id = fields.Many2one(comodel_name='res.partner', string="Customer Entity", readonly=True)
    country_id = fields.Many2one(comodel_name='res.country', string="Customer Country", readonly=True)
    industry_id = fields.Many2one(comodel_name='res.partner.industry', string="Customer Industry", readonly=True)
    partner_zip = fields.Char(string="Customer ZIP", readonly=True)
    state_id = fields.Many2one(comodel_name='res.country.state', string="Customer State", readonly=True)

    # Product-related fields
    categ_id = fields.Many2one(comodel_name='product.category', string="Product Category", readonly=True)
    product_id = fields.Many2one(comodel_name='product.product', string="Product Variant", readonly=True)
    product_tmpl_id = fields.Many2one(comodel_name='product.template', string="Product", readonly=True)
    product_uom = fields.Many2one(comodel_name='uom.uom', string="Unit of Measure", readonly=True)
    quantity = fields.Float(string="Qty Ordered", readonly=True)
    qty_to_sale = fields.Float(string="Qty To Deliver", readonly=True)
    saled_qty = fields.Float(string="Qty Delivered", readonly=True)
    subtotal = fields.Float(string="Subtotal", readonly=True)
    total = fields.Float(string="Total", readonly=True)
    unit_price = fields.Float(string="Unit Price", readonly=True)

    # Aggregate or computed fields
    nbr = fields.Integer(string="# of Lines", readonly=True)

    def _select_contract(self):
        return """
            MIN(l.id) AS id,
            s.name AS name,
            s.partner_id AS partner_id,
            s.user_id AS user_id,
            s.date AS date,
            s.company_id AS company_id,
            s.state AS state,
            partner.commercial_partner_id AS commercial_partner_id,
            partner.country_id AS country_id,
            partner.industry_id AS industry_id,
            partner.state_id AS state_id,
            partner.zip AS partner_zip,
            l.product_id AS product_id,
            t.categ_id AS categ_id,
            p.product_tmpl_id AS product_tmpl_id,
            t.uom_id AS product_uom,
            SUM(l.quantity) AS quantity,
            SUM(l.sale_quantity) AS saled_qty,
            SUM(l.qty_to_sale) AS qty_to_sale,
            SUM(l.subtotal) AS subtotal,
            SUM(l.unit_price) AS unit_price,
            COUNT(*) AS nbr,
            SUM(s.total) AS total
        """

    def _from_contract(self):
        return """
            sale_contract_line l
            JOIN sale_contract s ON s.id = l.contract_id
            JOIN res_partner partner ON s.partner_id = partner.id
            JOIN product_product p ON l.product_id = p.id
            JOIN product_template t ON p.product_tmpl_id = t.id
        """

    def _where_contract(self):
        return """
            s.state != 'cancel'
        """

    def _group_by_contract(self):
        return """
            s.name, 
            s.partner_id, 
            s.user_id, 
            s.date, 
            s.company_id, 
            s.total,
            s.state, 
            partner.commercial_partner_id, 
            partner.country_id, 
            partner.industry_id, 
            partner.state_id, 
            partner.zip, 
            l.product_id, 
            t.categ_id, 
            p.product_tmpl_id, 
            t.uom_id
        """

    def _query(self):
        return f"""
            SELECT {self._select_contract()}
            FROM {self._from_contract()}
            WHERE {self._where_contract()}
            GROUP BY {self._group_by_contract()}
        """

    @property
    def _table_query(self):
        return self._query()

    def init(self):
        """Initialize the database view for the report."""
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS ({self._query()})
        """)
