import base64
import io
from odoo.tools.misc import xlsxwriter
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PurchaseReciepts(models.TransientModel):
    _name = 'purchase.receipt'

    date_from = fields.Date('Date From', )
    date_to = fields.Date('Date To', )
    file_download = fields.Binary()
    file_name = fields.Char()

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        if self.date_to and self.date_from:
            if self.date_to < self.date_from:
                raise ValidationError(_('Date From cannot be greater than Date To'))

    @api.multi
    def print_purchase_receipts(self):
        lines = self.env['account.invoice.line'].search([
            ('invoice_id.date_invoice', '>=', self.date_from),
            ('invoice_id.date_invoice', '<=', self.date_to),
            ('invoice_id.state', 'not in', ['draft', 'cancel'])
        ])


        filename = 'Account Purchase Receipts.xls'
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        style_table_header = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '11px'})
        style_header = workbook.add_format({'font_size': '13px',  'bold': True, })
        worksheet = workbook.add_worksheet(filename)

        worksheet.merge_range(0, 0, 0, 3, 'Purchase Receipts',style_header)
        # Add a bold format to use to highlight cells.

        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 32)
        worksheet.set_column('F:F', 25)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 15)
        worksheet.set_column('K:K', 25)
        worksheet.set_column('L:L', 25)
        worksheet.set_column('M:M', 25)
        worksheet.set_column('N:N', 15)
        worksheet.set_column('O:O', 15)
        worksheet.set_column('P:P', 15)
        worksheet.set_column('Q:Q', 15)
        worksheet.set_column('R:R', 15)
        worksheet.set_column('S:S', 15)
        worksheet.set_column('T:T', 15)
        worksheet.set_column('U:U', 25)
        worksheet.set_column('V:V', 15)

        worksheet.write(1, 0, 'Purchase order NO',style_table_header)
        worksheet.write(1, 1, 'Receipt No',style_table_header)
        worksheet.write(1, 2, 'Receipt Date',style_table_header)
        worksheet.write(1, 3, 'Type of Receipt',style_table_header)
        worksheet.write(1, 4, 'Supplier',style_table_header)
        worksheet.write(1, 5, 'Item Name (Items)',style_table_header)
        worksheet.write(1, 6, 'UOM (Items)',style_table_header)
        worksheet.write(1, 7, 'Rate (Items)',style_table_header)
        worksheet.write(1, 8, 'Quantity',style_table_header)
        worksheet.write(1, 9, 'Amount (Items)',style_table_header)
        worksheet.write(1, 10, 'Discount % (Items)',style_table_header)
        worksheet.write(1, 11, 'Discount Amount (Items)',style_table_header)
        worksheet.write(1, 12, 'Amount after discount (Items)',style_table_header)
        worksheet.write(1, 13, 'Gross Total',style_table_header)
        worksheet.write(1, 14, 'Additional Discount %',style_table_header)
        worksheet.write(1, 15, 'Additional Discount Amount',style_table_header)
        worksheet.write(1, 16, 'Other charges',style_table_header)
        worksheet.write(1, 17, 'Grand Total',style_table_header)
        worksheet.write(1, 18, 'Status',style_table_header)
        worksheet.write(1, 19, 'Mod of payment',style_table_header)
        worksheet.write(1, 20, 'Paid to',style_table_header)
        worksheet.write(1, 21, 'Paid Amount',style_table_header)

        row = 2

        for line in lines:
            inv = line.invoice_id

            worksheet.write(row, 0, line.purchase_line_id.order_id.name or None)
            worksheet.write(row, 1, line.purchase_line_id.move_ids.picking_id.name or None)
            worksheet.write(row, 2, line.purchase_line_id.move_ids.date or None)
            worksheet.write(row, 3, line.purchase_line_id.move_ids.picking_id.picking_type_id.name or None)
            worksheet.write(row, 4, line.purchase_line_id.move_ids.picking_id.partner_id.name or None)
            worksheet.write(row, 5, line.purchase_line_id.move_ids.picking_id.product_id.name or None)
            worksheet.write(row, 6, line.purchase_line_id.move_ids.product_uom.name or None)
            worksheet.write(row, 7, line.purchase_line_id.move_ids.price_unit or None)
            worksheet.write(row, 8, line.purchase_line_id.move_ids.product_uom_qty or None)
            worksheet.write(row, 9, line.price_subtotal or None)
            discount_amount = line.price_subtotal * (line.discount / 100)
            worksheet.write(row, 10, line.discount or None)
            worksheet.write(row, 11, discount_amount or None)
            worksheet.write(row, 12, line.price_subtotal - discount_amount or None)
            worksheet.write(row, 13, line.price_subtotal - discount_amount or None)
            worksheet.write(row, 14, None)
            worksheet.write(row, 15, None)
            worksheet.write(row, 16, inv.amount_tax or None)
            worksheet.write(row, 17, inv.amount_total or None)
            worksheet.write(row, 18, line.purchase_line_id.move_ids.state or None)

            if inv.payment_ids:
                for payment in inv.payment_ids:
                    worksheet.write(row, 19, payment.journal_id.name or None)
                    worksheet.write(row, 20, payment.journal_id.display_name or None)
                    worksheet.write(row, 21, payment.amount or None)
                    row += 1
            else:
                row += 1

        workbook.close()
        output.seek(0)
        self.file_name = filename
        self.file_download = base64.encodestring(output.getvalue())
        # export_id = self.env['tax.reports'].c
        output.close()
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/?model=purchase.receipt&id={}&field=file_download&filename_field=name&download=true'.format(
                self.id),
        }



