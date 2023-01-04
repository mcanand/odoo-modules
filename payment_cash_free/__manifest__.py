# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payment Provider: Cash Free',
    'version': '1.0',
    'category': 'Accounting/Payment Providers',
    'sequence': 350,
    'summary': "Cash free payment",
    'depends': ['payment'],
    'data': [
        'views/payment_provider_views.xml',
        'views/payment_cashfree_template.xml',
        'data/payment_provider_data.xml',
    ],
    'application': False,
    'assets': {
        'web.assets_frontend': [

        ],
    },
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'license': 'LGPL-3',
}
