from odoo import models, fields, api, _
from odoo.http import request


class ProductTemplateInherited(models.Model):
    _inherit = 'product.template'

    is_product_pack = fields.Boolean(string="Is a package?")
    pack_product_ids = fields.One2many(
        'product.pack', 'pack_id',
        string='Bundle Products')


class PackOfProducts(models.Model):
    _name = 'product.pack'
    _order = "sequence,id"

    sequence = fields.Integer('Sequence', default=1)
    product_id = fields.Many2many('product.product', string="Products")
    qty = fields.Integer(string='Qty', default=1)
    pack_id = fields.Many2one('product.template')
    extra_amount = fields.Float(default=0.0)


class OrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    pack = fields.Boolean(string="is pack product")

    def write(self, vals):
        res = super(OrderLineInherit, self).write(vals)
        if vals.get('product_uom_qty'):
            if self.product_id.is_product_pack:
                for line in self.order_id.order_line:
                    if line.linked_line_id.id == self.id:
                        line.write({'product_uom_qty': vals.get('product_uom_qty')})
        return res


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, **kwargs):
        res = super(SaleOrderInherit, self)._cart_update(product_id, line_id, add_qty, set_qty)
        self.update_product_pack(product_id, res.get('line_id'), add_qty, set_qty)
        return res

    def update_product_pack(self, product_id, line_id, add_qty, set_qty):
        if self.env['product.product'].browse(product_id).is_product_pack:
            if add_qty or set_qty == None:
                arr = []
                line = self.env['sale.order.line'].browse(line_id)
                for pack in line.product_id.pack_product_ids:
                    for product in pack.product_id:
                        arr.append(product.id)
                for i in range(len(arr)):
                    self.write({'order_line': [(0, 0, {'product_id': arr[i],
                                                       'order_id': self.id,
                                                       'pack': True,
                                                       'linked_line_id': line_id})]})
