from odoo.tests import common


class TestAccountTaxEc(common.TransactionCase):
    def test_ec_withholding_rates_after_sri_20260301(self):
        company = self.env.ref("base.demo_company_ec")
        chart_template = self.env["account.chart.template"].with_company(company)

        expected_amounts = {
            "tax_withhold_profit_303": -10,
            "tax_withhold_profit_303A": -5,
            "tax_withhold_profit_304": -10,
            "tax_withhold_profit_304A": -10,
            "tax_withhold_profit_304B": -10,
            "tax_withhold_profit_304C": -10,
            "tax_withhold_profit_304D": -10,
            "tax_withhold_profit_307": -3,
            "tax_withhold_profit_308": -10,
            "tax_withhold_profit_309": -3,
            "tax_withhold_profit_310": -1,
            "tax_withhold_profit_311": -3,
            "tax_withhold_profit_312": -2,
            "tax_withhold_profit_312A": -1,
            "tax_withhold_profit_312C": -1.75,
            "tax_withhold_profit_314A": -10,
            "tax_withhold_profit_314B": -10,
            "tax_withhold_profit_314C": -10,
            "tax_withhold_profit_314D": -10,
            "tax_withhold_profit_319": -2,
            "tax_withhold_profit_320": -10,
            "tax_withhold_profit_322": -2,
            "tax_withhold_profit_343": -1,
            "tax_withhold_profit_343A": -2,
            "tax_withhold_profit_343B": -2,
            "tax_withhold_profit_343C": -2,
            "tax_withhold_profit_344A": -2,
            "tax_withhold_profit_344B": -2,
            "tax_withhold_profit_344C": -2,
            "tax_withhold_profit_3482": -5,
        }

        for xmlid, expected_amount in expected_amounts.items():
            tax = chart_template.ref(xmlid)
            self.assertTrue(tax.active, xmlid)
            self.assertEqual(tax.amount, expected_amount, xmlid)

    def test_ec_withholding_template_contains_recommended_new_codes(self):
        company = self.env.ref("base.demo_company_ec")
        chart_template = self.env["account.chart.template"].with_company(company)
        tax_data = chart_template._get_ec_new_account_tax()

        expected_amounts = {
            "tax_withhold_profit_323O": 0,
            "tax_withhold_profit_324A": -2,
            "tax_withhold_profit_324B": -2,
            "tax_withhold_profit_324C": -2,
            "tax_withhold_profit_332E": 0,
            "tax_withhold_profit_332F": 0,
            "tax_withhold_profit_332H": 0,
            "tax_withhold_profit_3480": -15,
        }

        for xmlid, expected_amount in expected_amounts.items():
            self.assertIn(xmlid, tax_data)
            self.assertEqual(float(tax_data[xmlid]["amount"]), expected_amount, xmlid)
