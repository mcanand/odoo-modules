{
    'name': 'Social Media LinkedIn',
    'version': '14.0.1.0.0',
    'category': 'Extra Tools',
    'author': 'SIGB',
    'website': 'https://www.sociusus.com',
    'license': '',
    'summary': 'Social Media LinkedIn Module',
    'description': 'Social Media LinkedIn Module',

    'depends': ['social_media_base'],
    'license': 'AGPL-3',
    'data': [
        # 'security/ir.model.access.csv',
        'data/social_media_linkedin_data.xml',
        'views/res_config_settings_view.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': True,
}