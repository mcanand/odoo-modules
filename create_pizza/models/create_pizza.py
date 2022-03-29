from odoo import fields, models


class CreatePizza(models.Model):
    _name = 'pizza.create'
    _description = 'custom pizza extras feilds'

    name = fields.Char(string="name")
    extras = fields.Many2many('product.product', required=True)