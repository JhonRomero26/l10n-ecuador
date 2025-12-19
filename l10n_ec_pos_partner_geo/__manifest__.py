# Copyright 2025 Odoo Community Association (OCA)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

{
    "name": "L10n EC POS Partner Geo",
    "version": "18.0.1.0.0",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-ecuador",
    "category": "Point of Sale",
    "license": "LGPL-3",
    "summary": "Load map_picker widget assets in POS",
    "depends": [
        "point_of_sale",
        "web_map_field",
        "l10n_ec_partner_geo",
    ],
    "data": [
        "views/pos_partner_view.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            # Ensure the field widget + templates/styles exist in the POS bundle
            "web_map_field/static/src/**/*.js",
            "web_map_field/static/src/**/*.xml",
            "web_map_field/static/src/**/*.scss",
        ],
    },
    "installable": True,
    "application": False,
}
