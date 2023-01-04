{
    'name': 'Social Media Dashboard',
    'version': '14.0.0.0.1',
    'category': 'Extra Tools',
    'author': 'SIGB',
    'website': 'https://www.sociusus.com',
    'license': '',
    'summary': 'Social Media Dashboard Module',
    'description': 'Social Media Dashboard Module',

    'depends': ['base', 'mail', 'social_media_base', 'web'],
    'license': 'AGPL-3',
    'data': [
        'views/assets.xml',
        # 'views/social_media_dashboard_view.xml',
    ],
    'demo': [],
    'qweb': ['static/src/xml/templates.xml'],
    'installable': True,
    'application': True,
    'auto_install': False
}
