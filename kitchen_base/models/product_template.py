####################################################
#   Company: Socius Innovative Global Brains
#   Copyright: Socius Innovative Global Brains
#   Website: https://www.sociusus.com/
####################################################

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    preparation_minutes = fields.Float('Preparation time in minutes')
