# -*- coding: utf-8 -*-
# from odoo import http


# class WebsiteCoupons(http.Controller):
#     @http.route('/website_coupons/website_coupons/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/website_coupons/website_coupons/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('website_coupons.listing', {
#             'root': '/website_coupons/website_coupons',
#             'objects': http.request.env['website_coupons.website_coupons'].search([]),
#         })

#     @http.route('/website_coupons/website_coupons/objects/<model("website_coupons.website_coupons"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('website_coupons.object', {
#             'object': obj
#         })
