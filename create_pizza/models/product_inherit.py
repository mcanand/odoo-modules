from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError


class ProductInherit(models.Model):
    _inherit = 'product.template'

    is_pizza_size_dough = fields.Boolean(string='Pizza Size & dough', default=False)
    is_pizza_sauce = fields.Boolean(string='Pizza Sauce', default=False)
    is_main_product = fields.Boolean(string='Create pizza(Main Product)', default=False)

    # @api.constrains('is_main_product')
    # def check_only_one(self):
    #     product = self.env['product.product'].search([('is_main_product', '=', True)])
    #     if product:
    #         raise ValidationError(_("create pizza product already created"))
