import base64
import io
from odoo.tools.misc import xlsxwriter
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class TaxInvoice(models.TransientModel):
    _name = 'tax.reports'

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
    def print_tax_invoice(self):
        lines = self.env['account.invoice.line'].search([
            ('invoice_id.date_invoice', '>=', self.date_from),
            ('invoice_id.date_invoice', '<=', self.date_to),
            ('invoice_id.state', 'not in', ['draft', 'cancel'])
        ])
        filename = 'Account sale invoice Report.xls'

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        style_table_header = workbook.add_format({'align': 'center', 'bold': True, 'font_size': '11px'})
        style_header = workbook.add_format({'font_size': '13px',  'bold': True, })
        worksheet = workbook.add_worksheet(filename)

        worksheet.merge_range(0, 0, 0, 3, 'POS Sales Invoice',style_header)
        # Add a bold format to use to highlight cells.

        worksheet.set_column('A:A', 15)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 32)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 15)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 15)
        worksheet.set_column('J:J', 15)
        worksheet.set_column('K:K', 15)
        worksheet.set_column('L:L', 15)
        worksheet.set_column('M:M', 15)
        worksheet.set_column('N:N', 15)
        worksheet.set_column('O:O', 15)
        worksheet.set_column('P:P', 15)
        worksheet.set_column('Q:Q', 15)
        worksheet.set_column('R:R', 15)
        worksheet.set_column('S:S', 15)
        worksheet.set_column('T:T', 32)
        worksheet.set_column('U:U', 15)

        worksheet.write(1, 0, 'Invoice No',style_table_header)
        worksheet.write(1, 1, 'Invoice Date',style_table_header)
        worksheet.write(1, 2, 'Type of Invoice(POS SALE/ CREDIT CUSTOMER INVOICE)',style_table_header)
        worksheet.write(1, 3, 'Customer',style_table_header)
        worksheet.write(1, 4, 'Item Name (Items)',style_table_header)
        worksheet.write(1, 5, 'UOM (Items)',style_table_header)
        worksheet.write(1, 6, 'Rate (Items)',style_table_header)
        worksheet.write(1, 7, 'Quantity',style_table_header)
        worksheet.write(1, 8, 'Amount (Items)',style_table_header)
        worksheet.write(1, 9, 'Discount % (Items)',style_table_header)
        worksheet.write(1, 10, 'Discount Amount (Items)',style_table_header)
        worksheet.write(1, 11, 'Amount after discount (Items)',style_table_header)
        worksheet.write(1, 12, 'Gross Total',style_table_header)
        worksheet.write(1, 13, 'Additional Discount %',style_table_header)
        worksheet.write(1, 14, 'Additional Discount Amount',style_table_header)
        worksheet.write(1, 15, 'Other charges',style_table_header)
        worksheet.write(1, 16, 'Grand Total',style_table_header)
        worksheet.write(1, 17, 'Status',style_table_header)
        worksheet.write(1, 18, 'Mod of payment',style_table_header)
        worksheet.write(1, 19, 'Paid to',style_table_header)
        worksheet.write(1, 20, 'Paid Amount',style_table_header)


        row = 2
        for line in lines:
            inv = line.invoice_id
            worksheet.write(row, 0, inv.number or None)
            worksheet.write(row, 1, inv.date_invoice or None)
            worksheet.write(row, 2, inv.type or None)
            worksheet.write(row, 3, inv.partner_id.name or None)
            worksheet.write(row, 4, line.product_id.display_name or None)
            worksheet.write(row, 5, line.uom_id.name or None)
            worksheet.write(row, 6, line.price_unit or None)
            worksheet.write(row, 7, line.quantity or None)
            worksheet.write(row, 8, line.price_subtotal or None)
            worksheet.write(row, 9, line.discount or None)
            discount_amount = line.price_subtotal * (line.discount / 100)
            worksheet.write(row, 10, discount_amount or None)
            worksheet.write(row, 11, line.price_subtotal - discount_amount or None)
            worksheet.write(row, 12, line.price_subtotal - discount_amount or None)
            worksheet.write(row, 13, None)
            worksheet.write(row, 14, None)
            worksheet.write(row, 15, inv.amount_tax or None)
            worksheet.write(row, 16, inv.amount_total or None)
            worksheet.write(row, 17, inv.state or None)


            if inv.payment_ids:
                for payment in inv.payment_ids:
                    worksheet.write(row, 18, payment.journal_id.name or None)
                    worksheet.write(row, 20, payment.amount or None)
                    worksheet.write(row, 19, payment.journal_id.display_name or None)
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
            'url': '/web/content/?model=tax.reports&id={}&field=file_download&filename_field=name&download=true'.format(
                self.id),
        }



