from odoo import http
from odoo.http import request
import xlsxwriter
from io import BytesIO


class XLSReportController(http.Controller):

    @http.route('/download/sale_report_xls', type='http', auth='user')
    def download_sale_report_xls(self, date_from, date_to, **kwargs):
        # Fetch the sale orders within the date range
        orders = request.env['sale.order'].sudo().search([
            ('date_order', '>=', date_from),
            ('date_order', '<=', date_to),
        ])
        order_lines = request.env['sale.order.line'].sudo().search(
            [("order_id", "in", orders.ids)]
        )
        total_quantity = sum(order_line.product_uom_qty for order_line in order_lines)
        total_subtotal = sum(order_line.price_subtotal for order_line in order_lines)

        # Create an Excel workbook in memory
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})
        sheet = workbook.add_worksheet('Sales Report')

        # Write headers
        headers = ['Sale Order', 'Customer', 'Date', 'Product Code', 'Product Name', 'Quantity', 'Subtotal']

        # Format of workbook line
        center_format1 = workbook.add_format(
            {"align": "center", "valign": "vcenter", "bold": True}
        )
        center_format1.set_bg_color("#D3D3D3")
        center_format2 = workbook.add_format(
            {"align": "center", "valign": "vcenter", "bold": True}
        )
        center_format2.set_bg_color("#48AAAD")

        center_format3 = workbook.add_format(
            {"align": "center", "valign": "vcenter", "bold": True}
        )
        date = workbook.add_format(
            {"align": "center", "valign": "left", "bold": True}
        )
        date.set_bg_color("#ADD8E6")
        number_format = workbook.add_format({'num_format': '0.00',"bold":True})

        sheet.set_column(1, 1, 20)
        sheet.set_column(1, 3, 10)

        sheet.merge_range("A1:G3", "Sale Report: %s" % orders.company_id.name, center_format1)
        sheet.merge_range("A5:G5", "Date From: %s" % date_from, date)
        sheet.merge_range("A7:G7", "End Date: %s" % date_to, date)

        sheet.write_row(9, 0, headers, center_format3)

        # Write data rows
        row = 10
        for order_line in order_lines:
            sheet.write(row, 0, order_line.order_id.name)
            sheet.write(row, 1, order_line.order_id.partner_id.name)
            sheet.write(row, 2, order_line.order_id.date_order.strftime('%d/%m/%Y'))
            sheet.write(row, 3, order_line.product_id.default_code or "")
            sheet.write(row, 4, order_line.product_template_id.name)
            sheet.write(row, 5, order_line.product_uom_qty)
            sheet.write(row, 6, order_line.price_subtotal)
            row += 1

        # Add formula for total sum
        sheet.write(row, 5, total_quantity, number_format)
        sheet.write(row, 6, total_subtotal, number_format)

        workbook.close()

        # Prepare XLS response
        output.seek(0)
        xls_data = output.getvalue()
        output.close()

        file_name = "sale_report_{}_to_{}.xlsx".format(date_from, date_to)

        # Return the file for download
        return request.make_response(
            xls_data,
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', 'attachment; filename=%s' % file_name),
            ],
        )
