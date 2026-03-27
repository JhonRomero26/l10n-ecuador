from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Canton(models.Model):
    _name = "l10n_ec_ote.canton"
    _description = "Cantons"
    _order = "code, name"

    _sql_constraints = [
        (
            "l10n_ec_ote_canton_code_uniq",
            "unique(code)",
            "The canton code must be unique.",
        ),
    ]

    state_id = fields.Many2one(
        "res.country.state",
        ondelete="restrict",
        string="Province",
        required=True,
        index=True,
    )
    country_id = fields.Many2one(
        "res.country",
        related="state_id.country_id",
        store=True,
        readonly=True,
    )
    name = fields.Char(string="Cantón", required=True)
    code = fields.Char(required=True, copy=False, index=True)
    parish_ids = fields.One2many("l10n_ec_ote.parish", "canton_id", string="Parishes")

    @api.constrains("state_id")
    def _check_state_country(self):
        ecuador = self.env.ref("base.ec")
        for record in self:
            if record.state_id.country_id != ecuador:
                raise ValidationError(
                    _("Cantons can only be created for Ecuadorian provinces.")
                )

    @api.constrains("code", "state_id")
    def _check_code(self):
        for record in self:
            if not record.code or not record.code.isdigit() or len(record.code) != 4:
                raise ValidationError(
                    _("The canton code must contain exactly 4 digits.")
                )
            state_prefix = (record.state_id.code or "").zfill(2)
            if state_prefix and record.code[:2] != state_prefix:
                raise ValidationError(
                    _(
                        "The canton code must start with the province code %(prefix)s.",
                        prefix=state_prefix,
                    )
                )

    @api.model
    def _get_next_code(self, state):
        state_prefix = (state.code or "").zfill(2)
        if not state_prefix.isdigit() or len(state_prefix) != 2:
            raise ValidationError(
                _(
                    "Province %(state)s must have a 2 digit numeric code.",
                    state=state.display_name,
                )
            )
        last_canton = self.search(
            [("state_id", "=", state.id)], order="code desc", limit=1
        )
        next_suffix = int(last_canton.code[-2:]) + 1 if last_canton else 1
        if next_suffix > 99:
            raise ValidationError(
                _(
                    "Province %(state)s has no remaining canton codes.",
                    state=state.display_name,
                )
            )
        return f"{state_prefix}{next_suffix:02d}"

    @api.model_create_multi
    def create(self, vals_list):
        states = self.env["res.country.state"]
        for vals in vals_list:
            if vals.get("state_id") and not vals.get("code"):
                vals["code"] = self._get_next_code(states.browse(vals["state_id"]))
        return super().create(vals_list)


class Parish(models.Model):
    _name = "l10n_ec_ote.parish"
    _description = "Parishes"
    _order = "code, name"

    _sql_constraints = [
        (
            "l10n_ec_ote_parish_code_uniq",
            "unique(code)",
            "The parish code must be unique.",
        ),
    ]

    canton_id = fields.Many2one(
        "l10n_ec_ote.canton",
        ondelete="restrict",
        string="Cantón",
        required=True,
        index=True,
    )
    state_id = fields.Many2one(
        "res.country.state",
        related="canton_id.state_id",
        store=True,
        readonly=True,
    )
    country_id = fields.Many2one(
        "res.country",
        related="state_id.country_id",
        store=True,
        readonly=True,
    )
    name = fields.Char(string="Parish", required=True)
    code = fields.Char(required=True, copy=False, index=True)

    @api.constrains("country_id")
    def _check_country(self):
        ecuador = self.env.ref("base.ec")
        for record in self:
            if record.country_id != ecuador:
                raise ValidationError(
                    _("Parishes can only be created for Ecuadorian cantons.")
                )

    @api.constrains("code", "canton_id")
    def _check_code(self):
        for record in self:
            if not record.code or not record.code.isdigit() or len(record.code) != 6:
                raise ValidationError(
                    _("The parish code must contain exactly 6 digits.")
                )
            canton_prefix = record.canton_id.code or ""
            if canton_prefix and record.code[:4] != canton_prefix:
                raise ValidationError(
                    _(
                        "The parish code must start with the canton code %(prefix)s.",
                        prefix=canton_prefix,
                    )
                )

    @api.model
    def _get_next_code(self, canton, parish_type):
        if parish_type not in {"urban", "rural"}:
            raise ValidationError(_("Parish type must be either urban or rural."))

        parishes = self.search([("canton_id", "=", canton.id)])
        suffixes = []
        for parish in parishes:
            if parish.code and parish.code[-2:].isdigit():
                suffix = int(parish.code[-2:])
                if parish_type == "urban" and suffix < 50:
                    suffixes.append(suffix)
                if parish_type == "rural" and suffix > 50:
                    suffixes.append(suffix)

        if parish_type == "urban":
            next_suffix = max(suffixes, default=0) + 1
            if next_suffix >= 50:
                raise ValidationError(
                    _(
                        "Canton %(canton)s has no remaining urban parish codes.",
                        canton=canton.display_name,
                    )
                )
        else:
            next_suffix = max(suffixes, default=50) + 1
            if next_suffix > 99:
                raise ValidationError(
                    _(
                        "Canton %(canton)s has no remaining rural parish codes.",
                        canton=canton.display_name,
                    )
                )

        return f"{canton.code}{next_suffix:02d}"

    @api.model_create_multi
    def create(self, vals_list):
        cantons = self.env["l10n_ec_ote.canton"]
        parish_type = self.env.context.get("l10n_ec_ote_parish_type")
        for vals in vals_list:
            if vals.get("canton_id") and not vals.get("code") and parish_type:
                vals["code"] = self._get_next_code(
                    cantons.browse(vals["canton_id"]), parish_type
                )
        return super().create(vals_list)
