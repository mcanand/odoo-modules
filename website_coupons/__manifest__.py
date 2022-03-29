# -*- coding: utf-8 -*-
{
    'name': "Website Coupons",
    'summary': """To generate website coupons""",
    'description': """To generate website coupons""",
    'author': "Socius",
    'website': "http://www.sociusus.com",
    'category': 'eCommerce',
    'version': '14.0',
    'depends': ['base', 'coupon', 'sale_coupon', 'sale_coupon_delivery'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/data.xml',
        'views/promo_program.xml',
        'views/templates.xml',
    ],
}
