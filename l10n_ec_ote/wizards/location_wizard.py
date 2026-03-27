from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CantonWizard(models.TransientModel):
    _name = "l10n_ec_ote.canton.wizard"
    _description = "Cantón Wizard"

    country_id = fields.Many2one(
        "res.country",
        string="Country",
        required=True,
        readonly=True,
        default=lambda self: self.env.ref("base.ec"),
    )
    state_id = fields.Many2one(
        "res.country.state",
        string="Province",
        required=True,
    )
    name = fields.Char(string="Cantón", required=True)
    code = fields.Char(compute="_compute_code")

    @api.depends("state_id")
    def _compute_code(self):
        canton_model = self.env["l10n_ec_ote.canton"]
        for wizard in self:
            wizard.code = (
                canton_model._get_next_code(wizard.state_id)
                if wizard.state_id
                else False
            )

    @api.constrains("country_id", "state_id")
    def _check_country(self):
        ecuador = self.env.ref("base.ec")
        for wizard in self:
            if wizard.country_id != ecuador or wizard.state_id.country_id != ecuador:
                raise ValidationError(_("Only Ecuadorian provinces are allowed."))

    def action_create_canton(self):
        self.ensure_one()
        canton = self.env["l10n_ec_ote.canton"].create(
            {
                "state_id": self.state_id.id,
                "name": self.name,
                "code": self.code,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Cantón"),
            "res_model": "l10n_ec_ote.canton",
            "view_mode": "form",
            "res_id": canton.id,
            "target": "current",
        }


class ParishWizard(models.TransientModel):
    _name = "l10n_ec_ote.parish.wizard"
    _description = "Parish Wizard"

    country_id = fields.Many2one(
        "res.country",
        string="Country",
        required=True,
        readonly=True,
        default=lambda self: self.env.ref("base.ec"),
    )
    state_id = fields.Many2one(
        "res.country.state",
        string="Province",
        required=True,
    )
    canton_id = fields.Many2one(
        "l10n_ec_ote.canton",
        string="Cantón",
        required=True,
    )
    parish_type = fields.Selection(
        [("urban", "Urbana"), ("rural", "Rural")],
        string="Tipo de parroquia",
        required=True,
        default="rural",
    )
    name = fields.Char(string="Parroquia", required=True)
    code = fields.Char(compute="_compute_code")

    @api.onchange("state_id")
    def _onchange_state_id(self):
        if self.canton_id and self.canton_id.state_id != self.state_id:
            self.canton_id = False

    @api.onchange("canton_id")
    def _onchange_canton_id(self):
        if self.canton_id and self.canton_id.state_id != self.state_id:
            self.state_id = self.canton_id.state_id

    @api.depends("canton_id", "parish_type")
    def _compute_code(self):
        parish_model = self.env["l10n_ec_ote.parish"]
        for wizard in self:
            if wizard.canton_id and wizard.parish_type:
                wizard.code = parish_model._get_next_code(
                    wizard.canton_id, wizard.parish_type
                )
            else:
                wizard.code = False

    @api.constrains("country_id", "state_id", "canton_id")
    def _check_location(self):
        ecuador = self.env.ref("base.ec")
        for wizard in self:
            if wizard.country_id != ecuador or wizard.state_id.country_id != ecuador:
                raise ValidationError(_("Only Ecuadorian provinces are allowed."))
            if wizard.canton_id.state_id != wizard.state_id:
                raise ValidationError(
                    _("The selected canton does not belong to the selected province.")
                )

    def action_create_parish(self):
        self.ensure_one()
        parish = (
            self.env["l10n_ec_ote.parish"]
            .with_context(l10n_ec_ote_parish_type=self.parish_type)
            .create(
                {
                    "canton_id": self.canton_id.id,
                    "name": self.name,
                    "code": self.code,
                }
            )
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Parroquia"),
            "res_model": "l10n_ec_ote.parish",
            "view_mode": "form",
            "res_id": parish.id,
            "target": "current",
        }
