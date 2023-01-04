# Company: giordano.ch AG
# Copyright by: giordano.ch AG
# https://giordano.ch/

{
    "name": "Gio Obstundgemuese Theme",
    "version": "15.0.1.0.0-beta1",
    "summary": "Custom Website Theme",
    "sequence": 10,
    "depends": [
        "base",
        "portal",
        "website",
        "website_sale",
        "web",
        "mass_mailing",
        "sale",
        "payment",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/header.xml",
        "views/footer.xml",
        "views/res_company.xml",
        "views/product_filter.xml",
        "views/product_detail.xml",
        "views/impressum.xml",
        "views/home.xml",
        "views/mailing_contact.xml",
        "views/obst_panorama_config.xml",
        "views/login_register.xml",
        "views/panorama_hotspot.xml",
        "views/portal.xml",
        "views/contactus.xml",
        "views/about.xml",
        "views/checkout.xml",
    ],
    "installable": True,
    "application": True,
    "assets": {
        "web.assets_frontend": [
            "/gio_obstgemuese_theme/static/src/js/header.js",
            "/gio_obstgemuese_theme/static/src/js/shop.js",
            "/gio_obstgemuese_theme/static/src/css/header.css",
            "/gio_obstgemuese_theme/static/src/css/shop.css",
            "/gio_obstgemuese_theme/static/src/css/product_detail.css",
            "/gio_obstgemuese_theme/static/src/css/impressum.css",
            "/gio_obstgemuese_theme/static/src/css/login_register.css",
            "/gio_obstgemuese_theme/static/src/css/cart.css",
            "/gio_obstgemuese_theme/static/src/css/pr_wizard.less",
            "/gio_obstgemuese_theme/static/src/js/cart.js",
            "/gio_obstgemuese_theme/static/src/js/impressum.js",
            "/gio_obstgemuese_theme/static/src/css/home.css",
            "/gio_obstgemuese_theme/static/src/css/portal.css",
            "/gio_obstgemuese_theme/static/src/css/contactus.css",
            "/gio_obstgemuese_theme/static/src/js/login_register.js",
            "/gio_obstgemuese_theme/static/src/js/checkout.js",
            "/gio_obstgemuese_theme/static/src/js/home.js",
            "/gio_obstgemuese_theme/static/src/js/newsletter.js",
            "/gio_obstgemuese_theme/static/src/js/portal.js",
            "/gio_obstgemuese_theme/static/src/js/contactus.js",
            "https://kit.fontawesome.com/845364ebbe.js",
            "https://cdnjs.cloudflare.com/ajax/libs/pannellum/2.5.6/pannellum.css",  # noqa
            "https://cdnjs.cloudflare.com/ajax/libs/pannellum/2.5.6/pannellum.js",  # noqa
            "https://polyfill.io/v3/polyfill.min.js",  # noqa
        ],
        "web.assets_backend": [
            "https://cdnjs.cloudflare.com/ajax/libs/pannellum/2.5.6/pannellum.css",  # noqa
            "https://cdnjs.cloudflare.com/ajax/libs/pannellum/2.5.6/pannellum.js",  # noqa
        ],
    },
    "auto_install": False,
    "pre_init_hook": "pre_init_check",
}
