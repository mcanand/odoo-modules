{
    'name': 'CONTACT FILTER',
    'summary': 'CONTACT SEGMENTS/FILTERS',
    'version': '14.0.0.1',
    'category': '',
    'license': 'AGPL-3',
    'author': 'SIGB',
    'depends': ['sale', 'base', 'contacts', 'website_delivery_type', 'website_sale', 'website', 'payment'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/contacts_filters.xml',

        # 'views/custom_button.xml',
        # 'views/sale_order_search_by_mail.xml',
    ],
    'qweb': ['static/src/xml/tepm.xml'],
    'demo': [],
    'installable': True,

}
