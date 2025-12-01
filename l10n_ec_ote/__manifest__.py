{
    'name': "Ecuadorian Geopolitical Division",
    'summary': "Ecuadorian Geopolitical Division data",
    'version': '18.0.1.0.0',
    'author': 'OCA',
    'maintainer': 'OCA',
    'website': 'https://github.com/OCA/l10n-ecuador',
    'license': 'AGPL-3',
    'category': 'Localization',
    'depends': [
        'base',
        'l10n_ec',
    ],
    'data': [
        'views/res_partner.xml',
        'data/l10n_ec_ote.canton.csv',
        'data/l10n_ec_ote.parish.csv',
        'data/res_country.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
