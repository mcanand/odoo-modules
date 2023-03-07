# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class ProductSupplierInfoInherit(models.Model):
    _inherit = 'product.supplierinfo'

    price2 = fields.Float(string="Price2")
