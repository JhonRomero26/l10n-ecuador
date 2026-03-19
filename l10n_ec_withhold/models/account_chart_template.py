from odoo import api, models

from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @api.model
    def _10n_ec_withhold_post_init(self):
        """
        Initial setup for Ecuadorian companies on first module install.
        Runs after installation because it cannot be loaded together
        with the l10n_ec chart of accounts.
        """
        all_companies = self.env["res.company"].search([("chart_template", "=", "ec")])
        for company in all_companies:
            Template = self.with_company(company)
            Template._load_data(
                {"account.journal": self._get_ec_new_account_journal_withhold()}
            )
        return True

    @template("ec", "account.journal")
    def _get_ec_new_account_journal_withhold(self):
        return self._parse_csv("ec", "account.journal", module="l10n_ec_withhold")
