{
    "name": "Order Bin",
    "summary": """order bin""",
    "category": "",
    "version": "1.0.15.0",
    "sequence": 1,
    "author": "SIGB",
    "description": """order bin""",
    "depends": ['base', 'sale', 'stock'],
    "data": [
        'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/order_bin.xml',
        'views/sale_order_view.xml',

    ],
    "installable": True,
    "auto_install": False,
}
