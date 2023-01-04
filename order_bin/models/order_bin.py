from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class CabinetManagement(models.Model):
    _name = 'order.bin'
    _description = 'Order bin'

    name = fields.Char('Name')
    sale_order = fields.Many2one('sale.order', string='Sale Order')
    total_qty = fields.Integer(string="Total Quantity", compute='call_function')
    ware_house_qty = fields.Integer(string="Warehouse Quantity", compute='call_function')
    state = fields.Selection([
        ('done', 'Completed'),
        ('in_progress', 'In Progress'),
        ('empty', 'Empty')], string='Status', default='empty', compute='compute_state')
    color = fields.Integer('Color')
    assigned = fields.Boolean(string='Assigned')

    @api.depends('total_qty', 'ware_house_qty', 'sale_order')
    def call_function(self):
        sale = self.env['sale.order']
        for rec in self:
            rec.ware_house_qty = 0
            rec.total_qty = 0
            order = sale.search([('order_bin_id', '=', rec.id)])
            if order:
                for ord in order:
                    rec.sale_order = ord.id
                for line in order.order_line:
                    rec.total_qty += line.product_uom_qty
                for pic_id in order.picking_ids:
                    if pic_id.state != 'cancel':
                        for move_line in pic_id.move_ids_without_package:
                            rec.ware_house_qty += move_line.quantity_done

    @api.depends('state')
    def compute_state(self):
        for rec in self:
            if rec.total_qty == rec.ware_house_qty:
                rec.state = 'done'
                rec.color = 10
                rec.assigned = False
            if rec.total_qty == 0 and rec.ware_house_qty == 0:
                rec.state = 'empty'
                rec.color = 0
                rec.sale_order = None
                rec.assigned = False
            if rec.total_qty != rec.ware_house_qty:
                rec.state = 'in_progress'
                rec.color = 9
                rec.assigned = True

    def go_to_delivery(self):
        val = []
        if self.sale_order.picking_ids:
            for i in self.sale_order.picking_ids:
                val.append(i.id)
            return {
                'name': _('Transfers'),
                'view_mode': 'tree,form',
                'res_model': 'stock.picking',
                'domain': [('id', 'in', val)],
                'view_id': False,
                'type': 'ir.actions.act_window',
                'context': {}
            }
        else:
            raise ValidationError(_('No order assigned'))
