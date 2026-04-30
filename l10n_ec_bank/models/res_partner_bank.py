from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

ACCOUNT_BANK_TYPE_SELECTION = [
    ("01", "Saving Account"),
    ("02", "Checking Account")
]


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    l10n_ec_account_bank_type = fields.Selection(
        selection=ACCOUNT_BANK_TYPE_SELECTION,
        string="Bank Type",
    )

    @api.constrains("partner_id", "l10n_ec_account_bank_type")
    def _check_l10n_ec_account_bank_type(self):
        for record in self:
            if record.country_code == "EC" and not record.l10n_ec_account_bank_type:
                raise ValidationError(
                    _("Bank Type is required for Ecuadorian bank accounts.")
                )
