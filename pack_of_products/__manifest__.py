# -*- coding: utf-8 -*-
{
    'name': 'Pack of Products',
    'version': '15.0.0.0',
    'sequence': 0,
    'category': 'Website',
    "author": "Socius IGB Pvt.Ltd.",
    "website": "http://www.socius.com",
    'license': 'LGPL-3',
    'description': """Website Product Packs""",
    'depends': ['base', 'product', 'sale', 'website_sale', 'sale_management', 'website'],
    'assets': {
        'web.assets_frontend': [
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/product_template.xml',
        'views/cart.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
