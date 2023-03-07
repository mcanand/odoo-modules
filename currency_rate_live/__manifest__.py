# -*- coding: utf-8 -*-
{
    'name': 'Live Currency Exchange Rate',
    'version': '15.0.1.0',
    'category': 'Accounting/Accounting',
    'author': 'Anand MC',
    'description': """Import exchange rates from the Internet.""",
    'depends': [
        'account',
    ],
    'data': [
        'views/res_config_settings_views.xml',
        'views/service_cron_data.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
