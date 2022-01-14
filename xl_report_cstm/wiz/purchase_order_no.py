import base64
import io
from odoo.tools.misc import xlsxwriter
from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError


class PurchaseOrderNo(models.TransientModel):
    _name = 'purchase.order.no'

    date_from = fields.Date('Date From', required=True)
    date_to = fields.Date('Date To', required=True)
    file_download = fields.Binary()
    file_name = fields.Char()

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        if self.date_to and self.date_from:
            if self.date_to < self.date_from:
                raise ValidationError(_('Date From cannot be greater than Date To'))

    @api.multi
    def print_purchase_order_no(self):
        lines = self.env['account.invoice.line'].search([
            ('invoice_id.date_invoice', '>=', self.date_from),
            ('invoice_id.date_invoice', '<=', self.date_to),
            ('invoice_id.state', 'not in', ['draft', 'cancel'])
        ])
        filename = 'Account Purchase Order No.xls'

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        style_table_header = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '11px'})
        style_header = workbook.add_format({'font_size': '13px',  'bold': True, })
        worksheet = workbook.add_worksheet(filename)

        # worksheet.merge_range(0, 0, 0, 3, 'Purchase Order',style_header)
        # Add a bold format to use to highlight cells.

        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 32)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 25)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 32)

        worksheet.write(1, 0, 'PO NUMBER', style_table_header)
        worksheet.write(1, 1, 'PO REFERENCE', style_table_header)
        worksheet.write(1, 2, 'SUPPLIER', style_table_header)
        worksheet.write(1, 3, 'ITEM DESCRIPTION', style_table_header)
        worksheet.write(1, 4, 'UOM', style_table_header)
        worksheet.write(1, 5, 'QTY', style_table_header)
        worksheet.write(1, 6, 'VALUE', style_table_header)

        row = 2
        for line in lines:
            inv = line.invoice_id
            worksheet.write(row, 0, line.purchase_line_id.order_id.name or None)
            worksheet.write(row, 1, line.purchase_line_id.order_id.partner_ref or None)
            worksheet.write(row, 2, line.purchase_line_id.order_id.partner_id.name or None)
            worksheet.write(row, 3, line.purchase_line_id.name or None)
            worksheet.write(row, 4, line.purchase_line_id.product_uom.name or None)
            worksheet.write(row, 5, line.purchase_line_id.product_uom_qty or None)
            worksheet.write(row, 6, line.purchase_line_id.product_id.name or None)
            row += 1

        workbook.close()
        output.seek(0)
        self.file_name = filename
        self.file_download = base64.encodestring(output.getvalue())
        # export_id = self.env['tax.reports'].c
        output.close()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=purchase.order.no&id={}&field=file_download&filename_field=name&download=true'.format(
                self.id),
        }



