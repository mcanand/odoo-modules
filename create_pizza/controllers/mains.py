from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleInherit(WebsiteSale):
    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, brands=None, **post):
        if category:
            if category.name == 'create a pizza':
                return request.redirect('/pizza/create')
        return super(WebsiteSaleInherit, self).shop(page=page, category=category, search=search, ppg=ppg, **post)


class CreatePizzaCustom(http.Controller):
    @http.route('/pizza/create', auth='public', type="http", website=True)
    def create_pizza_custom(self):
        product_size = request.env['product.product'].sudo().search([('is_pizza_size_dough', '=', True)])
        product_sauce = request.env['product.product'].sudo().search([('is_pizza_sauce', '=', True)])
        main_product = request.env['product.product'].sudo().search([('is_main_product', '=', True)])
        # extras = main_product.bundle_product_ids
        extras = request.env['pizza.create'].sudo().search([])
        return http.request.render('create_pizza.create_pizza_custom',
                                   {'pr_size_dough': product_size, 'pr_sauce': product_sauce, 'extras': extras,
                                    'main_prod': main_product})


class PizzaCreate(http.Controller):
    @http.route(['/create/pizza'], type='http', website=True, auth='public', methods=['POST'])
    def create(self, main_prod, redirect, size_dough, sauce, add_qty, **post):
        main_prod = int(main_prod)
        size_id = int(size_dough)
        sauce_id = int(sauce)
        add_qty = int(add_qty)
        size_id = request.env['product.product'].sudo().search([('id', '=', size_id)])
        sauce_id = request.env['product.product'].sudo().search([('id', '=', sauce_id)])
        main_prod = request.env['product.product'].sudo().search([('id', '=', main_prod)])
        sale_order = request.website.sale_get_order(force_create=True)
        sale = sale_order._cart_update(product_id=main_prod.id, add_qty=add_qty)
        print(sale_order.id)
        line_id = sale['line_id']
        sale_order._cart_update(product_id=size_id.id, add_qty=1, linked_line_id=line_id)
        sale_order._cart_update(product_id=sauce_id.id, add_qty=1, linked_line_id=line_id)
        valsn = []
        for m in post:
            i_id = request.env['product.product'].sudo().search([('id', '=', int(m))])
            sale_order._cart_update(product_id=i_id.id, add_qty=int(post[m]), linked_line_id=line_id)
        return request.redirect(redirect)
