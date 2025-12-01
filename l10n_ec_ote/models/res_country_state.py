from odoo import fields, models


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    canton_ids = fields.One2many(
        'l10n_ec_ote.canton', 'state_id', string='Cantons')
