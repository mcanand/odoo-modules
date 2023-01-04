####################################################
#   Company: Socius Innovative Global Brains
#   Copyright: Socius Innovative Global Brains
#   Website: https://www.sociusus.com/
####################################################

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # TODO website orders should use this field
    pickup_time = fields.Datetime('Pickup Time')
    preparation_time = fields.Datetime('Preparation Time')
    # TODO set state field as 'to_cancel' from website to request order cancellation.
    #  This should be possible for orders with lines only in kvs state 'waiting'.
    state = fields.Selection(selection_add=[('to_cancel', 'To Cancel')])
    # TODO choose pickup or delivery
    delivery_type = fields.Selection([('pickup', 'Pick Up'), ('delivery', 'Delivery')], string='Delivery Type', default='delivery')
