from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestL10nEcPartnerAutocomplete(TransactionCase):
    def setUp(self):
        super().setUp()
        ec_country = self.env.ref("base.ec")
        self.env.company.sudo().write({"country_id": ec_country.id})

    def test_create_with_numeric_name_triggers_autocomplete(self):
        calls = {"count": 0}

        def _fake_autocomplete(self_partner, vals):
            calls["count"] += 1
            vals.update({"name": "ACME S.A.", "email": "info@example.com"})

        with patch(
            "odoo.addons.l10n_ec_partner.models.res_partner.ResPartner._autocomplete_partner_data",
            new=_fake_autocomplete,
        ):
            partner = self.env["res.partner"].create(
                {
                    "name": "1718137159",  # 10 digits
                    "country_id": self.env.ref("base.ec").id,
                }
            )

        self.assertEqual(calls["count"], 1)
        self.assertEqual(partner.vat, "1718137159")
        self.assertEqual(partner.name, "ACME S.A.")
        self.assertEqual(partner.email, "info@example.com")

    def test_name_create_uses_autocomplete(self):
        def _fake_autocomplete(self_partner, vals):
            vals.update({"name": "John Doe"})

        with patch(
            "odoo.addons.l10n_ec_partner.models.res_partner.ResPartner._autocomplete_partner_data",
            new=_fake_autocomplete,
        ):
            partner_id, display_name = self.env["res.partner"].name_create("1718137159")

        self.assertTrue(partner_id)
        self.assertIn("John Doe", display_name)

    def test_onchange_vat_sets_is_company_and_ident_type(self):
        partner = self.env["res.partner"].new(
            {
                "country_id": self.env.ref("base.ec").id,
                "vat": "1799999999001",  # 13 digits, 3rd digit = 9 => company
            }
        )
        partner._onchange_vat_l10n_ec()
        self.assertTrue(partner.is_company)

        ruc = self.env.ref("l10n_ec.ec_ruc", raise_if_not_found=False)
        if ruc:
            self.assertEqual(partner.l10n_latam_identification_type_id, ruc)

    def test_write_sets_is_company_and_ident_type(self):
        partner = self.env["res.partner"].create(
            {
                "name": "Test Partner",
                "country_id": self.env.ref("base.ec").id,
                "vat": "1718137159",
            }
        )
        partner.write({"vat": "1799999999001"})
        self.assertTrue(partner.is_company)

        ruc = self.env.ref("l10n_ec.ec_ruc", raise_if_not_found=False)
        if ruc:
            self.assertEqual(partner.l10n_latam_identification_type_id, ruc)

    def test_make_request_without_requests_raises_translatable_error(self):
        partner = self.env["res.partner"].browse()
        with patch("odoo.addons.l10n_ec_partner.models.res_partner.requests", None):
            with self.assertRaises(UserError) as exc:
                partner.with_context(lang="en_US")._make_request(
                    "http://example.invalid"
                )

        self.assertIn("requests", str(exc.exception))
        self.assertIn("not installed", str(exc.exception).lower())

    def test_internal_user_can_run_autocomplete_without_settings_rights(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "l10n_ec_partner.api_url", "http://example.invalid/partner"
        )

        user = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "EC Partner User",
                    "login": "ec_partner_user",
                    "email": "ec_partner_user@example.com",
                    "groups_id": [(6, 0, [self.env.ref("base.group_user").id])],
                }
            )
        )

        class _FakeResponse:
            def json(self):
                return {"name": "Secure Partner"}

        partner = self.env["res.partner"].create(
            {
                "name": "Tmp",
                "vat": "1718137159",
                "country_id": self.env.ref("base.ec").id,
            }
        )

        vals = {"vat": "1718137159"}
        with patch(
            "odoo.addons.l10n_ec_partner.models.res_partner.ResPartner._make_request",
            return_value=_FakeResponse(),
        ):
            partner.with_user(user)._autocomplete_partner_data(vals)

        self.assertEqual(vals.get("name"), "Secure Partner")
