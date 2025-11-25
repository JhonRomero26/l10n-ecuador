from odoo import _, models
from odoo.exceptions import UserError


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _pre_render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        report = self._get_report(report_ref)
        if report.report_name == "l10n_ec_withhold.report_withhold_ec":
            not_wh_moves = (
                self.env["account.move"]
                .browse(res_ids)
                .filtered(lambda m: not m.l10n_ec_withholding_type)
            )
            if not_wh_moves:
                raise UserError(_("This document is not a withholding."))

        return super()._pre_render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
