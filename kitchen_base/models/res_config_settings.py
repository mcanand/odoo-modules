####################################################
#   Company: Socius Innovative Global Brains
#   Copyright: Socius Innovative Global Brains
#   Website: https://www.sociusus.com/
####################################################

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_pre_order = fields.Boolean('Enable Pre-Order')
    minimum_preparation_time = fields.Float('Minimum preparation time in minutes', default=10,
                                            config_parameter='kitchen_base.minimum_preparation_time')
