from odoo import fields, models


class Canton(models.Model):
    _name = "l10n_ec_ote.canton"
    _description = "Cantons"

    state_id = fields.Many2one(
        "res.country.state",
        ondelete="restrict",
        string="Province",
    )
    name = fields.Char(string="Canton")
    code = fields.Char()
    parish_ids = fields.One2many("l10n_ec_ote.parish", "canton_id", string="Parishes")


class Parish(models.Model):
    _name = "l10n_ec_ote.parish"
    _description = "Parishes"

    canton_id = fields.Many2one(
        "l10n_ec_ote.canton",
        ondelete="restrict",
        string="Canton",
    )
    name = fields.Char(string="Parish")
    code = fields.Char()
