####################################################
#   Company: Socius Innovative Global Brains
#   Copyright: Socius Innovative Global Brains
#   Website: https://www.sociusus.com/
####################################################

from odoo import fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    preparation_time = fields.Datetime('Preparation Time')
