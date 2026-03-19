from markupsafe import escape

from odoo import _, api, models
from odoo.tools.misc import format_amount


class AccountMoveSend(models.AbstractModel):
    _inherit = "account.move.send"

    @api.model
    def _get_default_mail_subject(self, move, mail_template, mail_lang):
        if move.l10n_ec_withholding_type:
            self = self.with_context(lang=mail_lang)
            return _(
                "%(company)s Withholding Certificate (Ref %(name)s)",
                company=move.company_id.name,
                name=move.name or "n/a",
            )
        return super()._get_default_mail_subject(move, mail_template, mail_lang)

    @api.model
    def _get_default_mail_body(self, move, mail_template, mail_lang):
        if move.l10n_ec_withholding_type:
            self = self.with_context(lang=mail_lang)
            related_invoices = move.line_ids.mapped("l10n_ec_invoice_withhold_id")
            invoice_total_amount = abs(sum(related_invoices.mapped("amount_total")))
            invoice_net_amount = abs(sum(related_invoices.mapped("amount_residual")))
            withhold_amount = sum(
                move.l10n_ec_withhold_line_ids.mapped("l10n_ec_withhold_tax_amount")
            )
            paid_amount = max(
                invoice_total_amount - withhold_amount - invoice_net_amount, 0.0
            )
            partner_name = escape(move.partner_id.name or "")
            parent_name = escape(move.partner_id.parent_id.name or "")
            company_name = escape(move.company_id.name or "")
            move_name = escape(move.name or "")
            invoice_names = escape(", ".join(related_invoices.mapped("name")))

            greeting = (
                f"{partner_name} ({parent_name}),"
                if move.partner_id.parent_id
                else f"{partner_name},"
            )
            invoice_reference = (
                _(
                    ", corresponding to invoice %(invoice)s issued by %(company)s.",
                    invoice=invoice_names,
                    company=company_name,
                )
                if related_invoices
                else _(" issued by %(company)s.", company=company_name)
            )
            summary_lines = [
                (
                    _("Invoice total:"),
                    format_amount(self.env, invoice_total_amount, move.currency_id)
                    or "",
                ),
                (
                    _("Amount withheld:"),
                    format_amount(self.env, withhold_amount, move.currency_id) or "",
                ),
            ]
            if paid_amount:
                summary_lines.append(
                    (
                        _("Amount paid:"),
                        format_amount(self.env, paid_amount, move.currency_id) or "",
                    )
                )
            if invoice_net_amount:
                summary_lines.append(
                    (
                        _("Net amount payable:"),
                        format_amount(self.env, invoice_net_amount, move.currency_id)
                        or "",
                    )
                )
            else:
                summary_lines.append((_("Invoice status:"), escape(_("Paid"))))
            summary_html = "".join(
                f"<br>- {escape(label)}"
                f' <span style="font-weight:bold">{value}</span>'
                for label, value in summary_lines
            )
            return f"""
<div style="margin:0px; padding:0px">
    <p style="margin:0px; padding:0px; font-size:13px">
        {escape(_('Dear'))}
            {greeting}
        <br><br>
        {escape(_('Attached is your withholding certificate'))}
            <span style="font-weight:bold">{move_name}</span>{invoice_reference}
        <br><br>
        {escape(_('Summary:'))}
        {summary_html}
        <br><br>
        {escape(_('Contact us if you have any questions.'))}
    </p>
</div>""".strip()
        return super()._get_default_mail_body(move, mail_template, mail_lang)

    @api.model
    def _get_default_mail_template_id(self, move):
        if move.l10n_ec_withholding_type:
            return self.env.ref("l10n_ec_withhold.email_template_edi_withhold")
        return super()._get_default_mail_template_id(move)

    @api.model
    def _check_move_constrains(self, moves):
        # Only check constrains for non-withholding moves
        moves_to_check = moves.filtered(lambda move: not move.is_purchase_withhold())
        if moves_to_check:
            return super()._check_move_constrains(moves_to_check)

    @api.model
    def _get_default_pdf_report_id(self, move):
        if move.l10n_ec_withholding_type:
            return self.env.ref("l10n_ec_withhold.action_report_withholding_ec")
        return super()._get_default_pdf_report_id(move)

    @api.model
    def _check_invoice_report(self, moves, **custom_settings):
        # Filter out withholdings from the check, as they use a non-invoice report
        moves = moves.filtered(lambda m: not m.l10n_ec_withholding_type)
        if not moves:
            return
        super()._check_invoice_report(moves, **custom_settings)
