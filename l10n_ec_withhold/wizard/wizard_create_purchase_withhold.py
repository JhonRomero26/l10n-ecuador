from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero

from ..models.data import TAX_SUPPORT


class WizardCreatePurchaseWithhold(models.TransientModel):
    _inherit = "l10n_ec.wizard.abstract.withhold"
    _name = "l10n_ec.wizard.create.purchase.withhold"
    _description = "Wizard Purchase withhold"

    withhold_line_ids = fields.One2many(
        comodel_name="l10n_ec.wizard.create.purchase.withhold.line",
        inverse_name="withhold_id",
        string="Lines",
        required=True,
    )
    withhold_totals = fields.Float(compute="_compute_total_withhold", store=True)

    @api.depends("withhold_line_ids.withhold_amount")
    def _compute_total_withhold(self):
        for record in self:
            record.withhold_totals = sum(
                record.withhold_line_ids.mapped("withhold_amount")
            )

    def _prepare_withholding_vals(self):
        withholding_vals = super()._prepare_withholding_vals()
        withholding_vals["l10n_ec_withholding_type"] = "purchase"
        return withholding_vals

    def _has_base_for_line(self, wline):
        """
        Debe existir al menos una línea de factura con soporte coincidente
        e impuestos.
        """
        inv = wline.invoice_id
        target_support = wline.l10n_ec_tax_support
        for il in inv.invoice_line_ids:
            support = il.l10n_ec_tax_support or inv.l10n_ec_tax_support
            if support == target_support and il.tax_ids:
                return True
        return False

    def _validate_withhold_bases(self):
        """Valida que existan bases imponibles coherentes por línea de retención."""
        self.ensure_one()
        if not self.withhold_line_ids:
            raise UserError(_("Please add some withholding lines before continue"))

        for wline in self.withhold_line_ids:
            if not self._has_base_for_line(wline):
                raise UserError(
                    _(
                        "The base amount for withholding is zero.\n"
                        "Review withholding lines with Tax Support: %s.\n"
                        "Please ensure the following:\n"
                        " - The tax support of the invoice lines (or Tax support "
                        "   on the invoice) is equal to Tax support of the "
                        "   withholding line.\n"
                        " - The invoice lines have taxes correctly configured "
                        "   (VAT or Profit).",
                        self._tax_support_label(wline.l10n_ec_tax_support),
                    )
                )

    def _post_link_and_reconcile(self, move, total_by_invoice, account_type):
        """
        Postea, linkea a facturas y reconcilia:
        - account_type: 'liability_payable' (compra) o 'asset_receivable' (venta)
        """
        invoices = self.withhold_line_ids.mapped("invoice_id")
        invoices.write({"l10n_ec_withhold_ids": [Command.link(move.id)]})
        self._try_reconcile_withholding_moves(move, invoices, account_type)
        move.line_ids.filtered("tax_ids").write({"l10n_ec_withhold_id": move.id})

    def button_validate(self):
        """
        Create a Purchase Withholding and try to reconcile with invoice
        """
        self.ensure_one()
        self._validate_withhold_bases()

        move = self._create_withholding_move()
        cmds, total_by_invoice = self._build_line_commands(move, counterpart="payable")
        move.write({"line_ids": cmds})
        move._post()
        self._post_link_and_reconcile(
            move, total_by_invoice, account_type="liability_payable"
        )
        return True


class WizardPurchaseWithholdLine(models.TransientModel):
    _inherit = "l10n_ec.wizard.abstract.withhold.line"
    _name = "l10n_ec.wizard.create.purchase.withhold.line"
    _description = "Wizard Purchase withhold line"

    withhold_id = fields.Many2one(
        comodel_name="l10n_ec.wizard.create.purchase.withhold",
        string="Withhold",
        ondelete="cascade",
    )
    l10n_ec_tax_support = fields.Selection(
        TAX_SUPPORT,
        string="Tax Support",
        copy=False,
    )

    @api.onchange("invoice_id", "tax_group_withhold_id", "l10n_ec_tax_support")
    def _onchange_withholding_base(self):
        res = {
            "value": {},
            "warning": {},
        }
        # replace function to compute base_amount considering l10n_ec_tax_support
        if not self.l10n_ec_tax_support or not self.tax_group_withhold_id:
            res["value"]["base_amount"] = 0.0
            return res
        currency_prec = self.invoice_id.company_id.currency_id.rounding
        base_amount = 0.0
        for invoice_line in self.invoice_id.invoice_line_ids:
            l10n_ec_tax_support = (
                invoice_line.l10n_ec_tax_support or self.invoice_id.l10n_ec_tax_support
            )
            if l10n_ec_tax_support == self.l10n_ec_tax_support and invoice_line.tax_ids:
                if (
                    self.tax_group_withhold_id.l10n_ec_type
                    == "withhold_income_purchase"
                ):
                    base_amount += abs(invoice_line.price_subtotal)
                elif self.tax_group_withhold_id.l10n_ec_type == "withhold_vat_purchase":
                    base_amount += abs(
                        invoice_line.price_total - invoice_line.price_subtotal
                    )
        if float_is_zero(base_amount, precision_rounding=currency_prec):
            res["value"]["base_amount"] = 0.0
            res["warning"] = {
                "title": _("User Information"),
                "message": _(
                    "The base amount for withholding is zero. "
                    "Please ensure the following:\n"
                    " - The tax support of the invoice lines"
                    "(or Tax support on the invoice) "
                    "is equal to Tax support of the withholding line.\n"
                    " - The invoice lines have taxes "
                    "correctly configured(VAT or Profit)."
                ),
            }
            return res
        self.base_amount = base_amount

    def _prepare_basis_vals(self, wizard, tax_data):
        vals = super()._prepare_basis_vals(wizard, tax_data)
        vals["l10n_ec_tax_support"] = self.l10n_ec_tax_support
        return vals
