from collections import defaultdict

from odoo import Command, _, api, fields, models


class WizardAbstractWithhold(models.AbstractModel):
    _name = "l10n_ec.wizard.abstract.withhold"
    _description = "Abstract Withhold Wizard"

    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
    )
    issue_date = fields.Date(
        string="Date",
        required=True,
    )
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal")
    document_number = fields.Char(
        required=False,
        size=17,
        store=True,
        readonly=False,
    )
    electronic_authorization = fields.Char(
        size=49,
        required=False,
    )
    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Related Document",
        readonly=True,
    )

    def _set_document_number(self, move):
        move._set_next_sequence()
        document_number = move.l10n_latam_document_number
        if move.is_purchase_withhold():
            move.ref = document_number

    def _prepare_withholding_vals(self):
        return {
            "journal_id": self.journal_id.id,
            "ref": self.document_number,
            "date": self.issue_date,
            "l10n_ec_electronic_authorization": self.electronic_authorization,
            "move_type": "entry",
            "l10n_latam_document_type_id": self.env.ref("l10n_ec.ec_dt_07").id,
            "partner_id": self.partner_id.id,
        }

    def _tax_support_label(self, value):
        selection = self.withhold_line_ids._fields["l10n_ec_tax_support"].selection
        return dict(selection).get(value)

    def _create_withholding_move(self):
        """Create withholding move, assign sequence/reference and return it."""
        vals = self._prepare_withholding_vals()
        move = self.env["account.move"].create(vals)
        self._set_document_number(move)
        return move

    def _build_line_commands(self, move, counterpart="payable"):
        """
        Build Command.create(...) entries for withholding lines:
        - Base lines + tax counterpart per withhold line.
        - One aggregated counterpart per invoice (totals).
        counterpart: 'payable' (purchase) or 'receivable' (sale)
        """
        self.ensure_one()
        cmds = []
        totals = defaultdict(float)

        for wline in self.withhold_line_ids:
            for tax_vals in wline._get_withholding_line_vals(self):
                cmds.append(Command.create(tax_vals))
            totals[wline.invoice_id] += abs(wline.withhold_amount)

        for invoice, total in totals.items():
            move_name = _(
                "RET: %(document_number)s Invoice: %(invoice_number)s",
                document_number=move.l10n_latam_document_number,
                invoice_number=invoice.l10n_latam_document_number,
            )
            if counterpart == "payable":
                # Purchase: debit to Pay (passive)
                debit, credit = total, 0.0
                account_id = self.partner_id.property_account_payable_id.id
            else:
                # Sell: credit to Receive (active)
                debit, credit = 0.0, total
                account_id = self.partner_id.property_account_receivable_id.id

            cmds.append(
                Command.create(
                    {
                        "partner_id": self.partner_id.id,
                        "account_id": account_id,
                        "l10n_ec_invoice_withhold_id": invoice.id,
                        "name": move_name,
                        "debit": debit,
                        "credit": credit,
                    }
                )
            )

        return cmds, totals

    def _try_reconcile_withholding_moves(self, withholding, invoice, account_type):
        if account_type not in ["asset_receivable", "liability_payable"]:
            raise ValueError(
                "account_type must be 'asset_receivable' or 'liability_payable', "
                f"got {account_type!r}"
            )
        aml_to_reconcile = invoice.line_ids.filtered(
            lambda line: line.account_id.account_type == account_type
        )
        aml_to_reconcile += withholding.line_ids.filtered(
            lambda line: line.account_id.account_type == account_type
            and line.l10n_ec_invoice_withhold_id == invoice
        )
        aml_to_reconcile.reconcile()
        return True


class WizardAbstractWithholdLine(models.AbstractModel):
    _name = "l10n_ec.wizard.abstract.withhold.line"
    _description = "Wizard Abstract withhold line"

    tax_group_withhold_id = fields.Many2one(
        comodel_name="account.tax.group",
        string="Withholding Type",
    )
    tax_withhold_id = fields.Many2one(
        comodel_name="account.tax",
        string="Withholding tax",
    )
    base_amount = fields.Float(string="Amount Base", digits="Account", readonly=True)
    withhold_amount = fields.Float(
        string="Amount Withhold",
        digits="Account",
        compute="_compute_withholding_amount",
        store=True,
    )
    invoice_id = fields.Many2one("account.move")

    @api.onchange("invoice_id", "tax_group_withhold_id")
    def _onchange_withholding_base(self):
        for line in self:
            if line.tax_group_withhold_id.l10n_ec_type in [
                "withhold_income_sale",
                "withhold_income_purchase",
            ]:
                line.base_amount = abs(line.invoice_id.amount_untaxed_signed)
            elif line.tax_group_withhold_id.l10n_ec_type in [
                "withhold_vat_sale",
                "withhold_vat_purchase",
            ]:
                line.base_amount = abs(line.invoice_id.amount_tax_signed)

    @api.depends("invoice_id", "tax_withhold_id", "base_amount")
    def _compute_withholding_amount(self):
        for line in self:
            line.withhold_amount = abs(
                line.base_amount * line.tax_withhold_id.amount / 100
            )

    @api.onchange("tax_group_withhold_id")
    def onchange_tax_group_withhold(self):
        self.tax_withhold_id = False

    def _get_withholding_line_vals(self, wizard):
        taxes_data = self.tax_withhold_id.compute_all(self.base_amount)
        tax_vals = []
        for tax_data in taxes_data.get("taxes"):
            tax_vals.append(self._prepare_basis_vals(wizard, tax_data))
            tax_vals.append(self._prepare_basis_counterpart_vals(wizard, tax_data))
        return tax_vals

    def _prepare_basis_vals(self, wizard, tax_data):
        debit = credit = 0.0
        if self.invoice_id.move_type == "out_invoice":
            credit = abs(tax_data.get("base"))
        if self.invoice_id.move_type == "in_invoice":
            debit = abs(tax_data.get("base"))
        return {
            "partner_id": wizard.partner_id.id,
            "quantity": 1.0,
            "price_unit": abs(tax_data.get("base")),
            "account_id": tax_data.get("account_id"),
            "name": f"RET {wizard.document_number}",
            "debit": debit,
            "credit": credit,
            "tax_ids": [(6, 0, self.tax_withhold_id.ids)],
            "display_type": "product",
            "l10n_ec_invoice_withhold_id": self.invoice_id.id,
        }

    def _prepare_basis_counterpart_vals(self, wizard, tax_data):
        debit = credit = 0.0
        if self.invoice_id.move_type == "out_invoice":
            debit = abs(tax_data.get("base"))
        if self.invoice_id.move_type == "in_invoice":
            credit = abs(tax_data.get("base"))
        return {
            "partner_id": wizard.partner_id.id,
            "quantity": 1.0,
            "price_unit": abs(tax_data.get("base")),
            "account_id": tax_data.get("account_id"),
            "name": _("Counterpart RET %s", wizard.document_number),
            "debit": debit,
            "credit": credit,
            "tax_ids": [],
            "tax_tag_ids": [],
        }
