{
    "name": "Guest Checkout",
    "summary": """guest user checkout""",
    "category": "",
    "version": "1.0.15.0",
    "sequence": 10,
    "author": "SIGB",
    "description": """checks weather the same user is shopping again with same email""",
    "depends": ['base', 'website_sale'],
    "data": [
        'views/add_country_code.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            '/guest_checkout/static/src/js/checkout_country_code.js',
            '/guest_checkout/static/src/css/main.css',
        ],
        'web.assets_backend': [
            '/guest_checkout/static/src/css/main.css',
        ],
        'web.assets_common': [
            '/guest_checkout/static/src/css/main.css',
        ],
    },
    "installable": True,
    "auto_install": False,
}
