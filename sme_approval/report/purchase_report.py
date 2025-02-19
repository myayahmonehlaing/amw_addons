# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

#
# Please note that these reports are not multi-currency !!!
#

from odoo import fields, models, api


class PurchaseReport(models.Model):
    _inherit = "purchase.report"



    purchase_currency_id =  fields.Many2one("res.currency",readonly=True,string="Purchase Currency")
    currency_total = fields.Monetary(string='Currency Total', currency_field='purchase_currency_id', readonly=True)

    def _select(self):
        select_str = """
               SELECT
                   po.id as order_id,
                   min(l.id) as id,
                   po.date_order as date_order,
                   po.state,
                   po.date_approve,
                   po.dest_address_id,
                   po.partner_id as partner_id,
                   po.user_id as user_id,
                   po.company_id as company_id,
                   po.fiscal_position_id as fiscal_position_id,
                   l.product_id,
                   p.product_tmpl_id,
                   t.categ_id as category_id,
                   c.currency_id,
                   t.uom_id as product_uom,
                   extract(epoch from age(po.date_approve,po.date_order))/(24*60*60)::decimal(16,2) as delay,
                   extract(epoch from age(l.date_planned,po.date_order))/(24*60*60)::decimal(16,2) as delay_pass,
                   count(*) as nbr_lines,
                   sum(l.price_total / COALESCE(currency_table.rate, 1.0))::decimal(16,2) * po.currency_rate  as price_total, 
                   (sum(l.product_qty * l.price_unit / COALESCE(currency_table.rate, 1.0))/NULLIF(sum(l.product_qty/line_uom.factor*product_uom.factor),0.0))::decimal(16,2)
                    * po.currency_rate  as price_average,
                   partner.country_id as country_id,
                   partner.commercial_partner_id as commercial_partner_id,
                   sum(p.weight * l.product_qty/line_uom.factor*product_uom.factor) as weight,
                   sum(p.volume * l.product_qty/line_uom.factor*product_uom.factor) as volume,
                   sum(l.price_subtotal / COALESCE(currency_table.rate, 1.0))::decimal(16,2) * po.currency_rate  as untaxed_total,
                   sum(l.product_qty / line_uom.factor * product_uom.factor) as qty_ordered,
                   sum(l.qty_received / line_uom.factor * product_uom.factor) as qty_received,
                   sum(l.qty_invoiced / line_uom.factor * product_uom.factor) as qty_billed,
                   case when t.purchase_method = 'purchase' 
                        then sum(l.product_qty / line_uom.factor * product_uom.factor) - sum(l.qty_invoiced / line_uom.factor * product_uom.factor)
                        else sum(l.qty_received / line_uom.factor * product_uom.factor) - sum(l.qty_invoiced / line_uom.factor * product_uom.factor)
                   end as qty_to_be_billed,
                   po.currency_id  as  purchase_currency_id , 
                   spt.warehouse_id as picking_type_id, 
                   po.effective_date as effective_date,
                   sum(l.price_subtotal) as currency_total
       """
        return select_str



    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", po.currency_id"

