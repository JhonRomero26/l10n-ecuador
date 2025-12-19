{
    "name": "L10n EC Partner Geolocation",
    "version": "18.0.1.0.0",
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/l10n-ecuador",
    "category": "Sales/CRM",
    "license": "LGPL-3",
    "summary": "Adds geolocation features to the partner.",
    "depends": [
        "contacts",
        "base_geolocalize",
        "web_map_field",
        "l10n_ec_ote",
    ],
    "data": [
        "views/res_partner_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
