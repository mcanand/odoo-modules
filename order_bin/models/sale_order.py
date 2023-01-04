from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_bin_id = fields.Many2one('order.bin', string='Order Bin', index=True, copy=False)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        order_bin = self.env['order.bin']
        order_bins = order_bin.search([('sale_order', '=', self.id)])
        if order_bins.sale_order.id == self.id:
            return res
        else:
            order_bin_vals = order_bin.search([('assigned', '=', False)])
            empty = []
            done = []
            if order_bin_vals:
                for rec in order_bin_vals:
                    if rec.state == 'empty':
                        empty.append(rec.id)
                    elif rec.state == 'done':
                        done.append(rec.id)
            if empty:
                for i in empty:
                    self.order_bin_id = i
                    order_bin.search([('id', '=', i)]).write({'sale_order': self.id, 'assigned': True})
                    return res
            else:
                for j in done:
                    order_assigned = self.search([('order_bin_id', '=', j)])
                    order_assigned.order_bin_id = None
                    self.order_bin_id = j
                    order_bin.search([('id', '=', j)]).write({'sale_order': self.id, 'assigned': True})
                    return res

            # create a new slot in if no space availiable
            # else:
            #     new_slot = order_bin.create({'sale_order': self.id, 'assigned': True})
            #     self.order_bin_id = new_slot.id
        return res
