from odoo import api, fields, models

from .data import TAX_SUPPORT


class ResPartner(models.Model):
    _inherit = "res.partner"

    l10n_ec_avoid_withhold = fields.Boolean(
        related="property_account_position_id.l10n_ec_avoid_withhold",
    )
    l10n_ec_taxpayer_type_id = fields.Many2one(
        comodel_name="l10n_ec.taxpayer.type",
        string="SRI Taxpayer Type",
        help=(
            "Classifies the partner according to SRI taxpayer type and allows "
            "suggesting withholding taxes automatically."
        ),
    )
    l10n_ec_tax_support = fields.Selection(
        TAX_SUPPORT, string="Tax Support", help="Tax support in invoice line"
    )

    @api.model
    def _commercial_fields(self):
        return super()._commercial_fields() + ["l10n_ec_taxpayer_type_id"]
