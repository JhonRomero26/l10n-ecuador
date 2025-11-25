from odoo import api, models


class AccountMoveSend(models.AbstractModel):
    _inherit = "account.move.send"

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
