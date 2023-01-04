####################################################
#   Company: Socius Innovative Global Brains
#   Copyright: Socius Innovative Global Brains
#   Website: https://www.sociusus.com/
####################################################

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    preparation_minutes = fields.Float('Preparation time in minutes')
