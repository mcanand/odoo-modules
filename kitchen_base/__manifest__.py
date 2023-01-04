# -*- coding: utf-8 -*-
####################################################
#   Company: Socius Innovative Global Brains
#   Copyright: Socius Innovative Global Brains
#   Website: https://www.sociusus.com/
####################################################

{
    'name': 'Point of Sale Kitchen Base 14',
    'version': '1.0.1',
    'category': 'Sales/Point of Sale',
    'sequence': 1,
    'summary': '',
    'summary': "PoS module for pre order configuration and base for kitchen order module.",
    'author': 'SIGB',
    'company': 'SIGB',
    'maintainer': 'SIGB',
    'website': 'https://sociusus.com',
    'depends': ['base', 'point_of_sale', 'sale', 'stock', 'product'],
    'data': [
        # 'views/product_product.xml',
        'views/product_template.xml',
        'views/res_config_settings.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
    'application': False,
    'qweb': [],
}
