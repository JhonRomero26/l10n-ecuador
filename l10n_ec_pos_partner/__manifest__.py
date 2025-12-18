{
    "name": "L10N EC POS Partner",
    "version": "18.0.1.0.0",
    "summary": "Customizes the customer creation flow in the Point of Sale.",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-ecuador",
    "license": "LGPL-3",
    "category": "Point of Sale",
    "depends": ["point_of_sale", "l10n_ec_partner"],
    "assets": {
        "point_of_sale._assets_pos": [
            "l10n_ec_pos_partner/static/src/**/*",
        ],
    },
    "installable": True,
    "application": False,
}
