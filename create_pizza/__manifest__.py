{
    'name': 'CUSTOM PIZZA CREATION',
    'summary': 'create custom pizza',
    'version': '14.0.1.0',
    'category': '',
    'license': 'LGPL-3',
    'author': 'SOCIUS',
    'depends': ['web', 'website','stock','website_rfg','contacts'],
    'data': [
        'views/assets.xml',
        'security/ir.model.access.csv',
        'views/custom_pizza_fields.xml',
        'views/create_pizza.xml',
        'views/custom_pizza.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
