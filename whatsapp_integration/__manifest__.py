# -*- coding: utf-8 -*-
{
    'name': 'Whatsapp Odoo Integration',
    'summary': 'Integration of Whatsapp for Sale, CRM, Invoice, Delivery and more, send message through whatsapp',
    'version': '15.0.1.0.0',
    'category': 'Administration',
    'author': 'SIGB',
    'license': 'OPL-1',
    'depends': [
        'base',
        'web',
        'crm',
        'sale_management',
        'sales_team',
        'purchase',
        'account',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/data_whatsapp_default.xml',

        'views/res_config_settings.xml',
        'views/whatsapp_templates.xml',
        'views/view_integration_sale.xml',
        'views/view_integration_res_user.xml',
        'views/view_integration_events.xml',

        'wizard/wizard_whatsapp_sale.xml',
        'wizard/whatsapp_res_users.xml',
        'wizard/whatsapp_event_registration.xml',
        'templates/templates.xml',
    ],
    'images': ['static/description/icon.png'],
    'application': True,
    'installable': True,
    'assets': {
        'web.assets_backend': [

        ],
    },

}
