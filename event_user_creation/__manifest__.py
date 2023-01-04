{
    'name': 'Event User Creation',
    'summary': 'creating a user on registration in website with mobile number or email',
    'version': '15.0.1.0.0',
    'category': 'Administration',
    'author': 'SIGB',
    'license': '',
    'depends': [
        'base',
        'web',
        'website_event',
    ],
    'data': [
        'views/web_event_register.xml',
        'views/event_registration.xml',
    ],
    'images': ['static/description/icon.png'],
    'application': True,
    'installable': True,
    'assets': {
        'web.assets_backend': [

        ],
        'web.assets_frontend': [
            'event_user_creation/static/src/js/event_selection.js',
        ]
    },

}
