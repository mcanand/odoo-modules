from odoo import api, fields, models, _
import string


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    parameter_x = fields.Integer(string="Order bin Parameter X",
                                 readonly=False, default=0)
    parameter_y = fields.Integer(string="Order bin Parameter Y",
                                 readonly=False, default=0)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(parameter_x=self.env['ir.config_parameter'].sudo().get_param('cabinet_management.parameter_x')
                   )
        res.update(parameter_y=self.env['ir.config_parameter'].sudo().get_param('cabinet_management.parameter_y')
                   )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        parameter_x = self.parameter_x
        parameter_y = self.parameter_y
        param.set_param('cabinet_management.parameter_x', parameter_x)
        param.set_param('cabinet_management.parameter_y', parameter_y)

    def execute(self):
        self.ensure_one()
        alpha_order = list(string.ascii_uppercase)
        cabinets = self.env['order.bin'].search([('name', '!=', False)])
        x = int(self.env['ir.config_parameter'].sudo().get_param('order_bin.parameter_x'))
        y = int(self.env['ir.config_parameter'].sudo().get_param('order_bin.parameter_y'))
        if x != self.parameter_x or y != self.parameter_y:
            if self.parameter_x > 0 and self.parameter_y > 0:
                for cab in cabinets:
                    cab.unlink()
                alpha_list = alpha_order[:self.parameter_x]
                for x in range(self.parameter_x):
                    for y in range(self.parameter_y):
                        vals = {
                            'name': alpha_list[x] + str(y+1),
                            'state': 'empty',
                        }
                        cab = self.env['order.bin'].create(vals)
        return super(ResConfigSettings, self).execute()
