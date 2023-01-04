####################################################
#   Company: Socius Innovative Global Brains
#   Copyright: Socius Innovative Global Brains
#   Website: https://www.sociusus.com/
####################################################

from odoo import fields, models


class PosOrderLine(models.Model):
    _inherit = 'pos.order.line'

    kvs_state = fields.Selection(selection=[("pending", "Pending"),
                                            ("waiting", "Waiting"),
                                            ("preparing", "Preparing"),
                                            ("ready", "Ready for Delivery"),
                                            ("done", "Done"),
                                            ("cancel", "Cancel"),
                                            ("return", "Return")],
                                 default="pending")
