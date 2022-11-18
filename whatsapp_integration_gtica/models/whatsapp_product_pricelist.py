# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
from odoo.tools import float_round


class whatsapp_report_product_pricelist(models.AbstractModel):
    _name = 'report.whatsapp_product_list'
    _description = 'Product Price List Report Whatsapp'

    @api.model
    def get_report_values(self, price_list, qty, product_categories_ids):
        pricelist = self.env['product.pricelist'].browse(price_list.id)

        if not pricelist:
            return False

        products = self.env['product.product'].search([('active', '=', True), ('sale_ok', '=', True), ('categ_id', 'child_of', product_categories_ids.ids)])
        quantities = qty
        values = {
            'docs': products,
            'data': dict(
                pricelist=pricelist,
                quantities=quantities,
                categories_data=self._get_categories(pricelist, products, quantities)
                ),
            }

        return values


    def _get_quantity(self, data):
        form = data and data.get('form') or {}
        return sorted([form[key] for key in form if key.startswith('qty') and form[key]])

    def _get_categories(self, pricelist, products, quantities):
        categ_data = []

        categories = self.env['product.category']

        for product in products:
            categories |= product.categ_id

        for category in categories:
            categ_products = products.filtered(lambda product: product.categ_id == category)
            prices = {}
            for categ_product in categ_products:
                prices[categ_product.id] = dict.fromkeys(quantities, 0.0)
                for quantity in quantities:
                    prices[categ_product.id][quantity] = self._get_price(pricelist, categ_product, quantity)
            categ_data.append({
                'category': category,
                'products': categ_products,
                'prices': prices,
            })
        return categ_data

    def _get_price(self, pricelist, product, qty):
        sale_price_digits = self.env['decimal.precision'].precision_get('Product Price')
        price = pricelist.get_product_price(product, qty, False)
        if not price:
            price = product.list_price
        return float_round(price, precision_digits=sale_price_digits)
