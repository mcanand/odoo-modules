from odoo import fields, models, _
import xlrd
import base64
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from datetime import date


class UploadExcelFile(models.TransientModel):
    _name = 'excel.upload'

    file = fields.Binary(string="Choose Excel")

    def get_psn_format(self, value):
        if type(value) != str:
            return str(int(value))
        return value

    def create_excel_import(self):
        """button function of import xl to create records in
        'excel.import.custom' model before creating get_xl_data"""
        if self.file:
            xl_data = self.get_xl_data(self.file)
            import_model = self.env['excel.import.custom']
            xl_import = import_model.search([('id', '=', self.id)])
            no = 0
            for val in xl_data:
                data = self.check_datas(val)
                if data:
                    vals = {'excel_import_custom_id': self.id,
                            'sl_no': no + 1,
                            'file_name': val.get('file_name'),
                            'psn': self.get_psn_format(val.get('psn')),
                            'payable': val.get('payable'),
                            'agent_score': val.get('agent_score'),
                            'claimed': val.get('claimed'),
                            'reason': val.get('reason') if val.get(
                                'reason') else ''}
                    try:
                        xl_import.write({
                            'name': 'ENTRY/' + str(self.id) + '/' + str(
                                date.today()),
                            'state': 'ready',
                            'sale_data_entry_ids': [(0, 0, vals)]
                        })
                        no = no + 1
                    except Exception as e:
                        raise ValidationError(_(e))
        else:
            raise ValidationError(
                _("Please upload xlsx file to create entries"))

    def check_datas(self, val):
        """Check required field are filled in xl file and
        check file name is unique"""
        sale_data_entry = self.env['sale.data.entries']
        if val.get('file_name') == '':
            raise ValidationError(
                _("Couldn't find file name, Please check your xlsx"))
        else:
            data_entry = sale_data_entry.search(
                [('file_name', '=', val.get('file_name')),
                 ('state', '=', 'done')])
            if data_entry:
                raise ValidationError(
                    _(data_entry.file_name + " file name already exist please check"
                                             ", change or remove the entry from xlsx"))
        if val.get('psn') == '':
            raise ValidationError(
                _("Couldn't find PSN No for" + val.get(
                    'file_name') + ", Please check your xlsx"))
        if val.get('payable') == '':
            raise ValidationError(
                _("Couldn't find Net Payable Page/Record,"
                  " Please check your xlsx"))
        if val.get('agent_score') == '':
            raise ValidationError(
                _("Couldn't find Agent Score,"
                  " Please check your xlsx"))
        if val.get('claimed') == '':
            raise ValidationError(
                _("Couldn't find Agent Claimed Page/Record,"
                  " Please check your xlsx"))
        return True

    def get_xl_data(self, file):
        """get data from xl and convert it to dictionary
        converting binary datatype using xlrd to read xlsx file"""
        file_data = base64.b64decode(self.file)
        book = xlrd.open_workbook(file_contents=file_data)
        line_vals = []
        for sheet in book.sheets():
            keys = sheet.row_values(0)
            for row in range(sheet.nrows)[1:]:  # [1,A],[2,B]
                vals = dict(zip(keys, sheet.row_values(row)))
                line_vals.append(vals)
        return line_vals
