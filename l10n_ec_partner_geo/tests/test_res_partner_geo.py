from unittest.mock import patch

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestL10nEcPartnerGeo(TransactionCase):
    def setUp(self):
        super().setUp()
        # Ensure company is Ecuador to exercise EC-specific flows
        self.env.company.sudo().write({"country_id": self.env.ref("base.ec").id})

    def test_onchange_map_picker_data_parses_json(self):
        partner = self.env["res.partner"].new({})
        data = {
            "lat": "-1.234",
            "lon": "-78.456",
            "precision": "house",
            "city": "Quito",
            "street": "Main St",
        }
        partner.map_picker_data = data
        # call the onchange method
        partner._onchange_map_picker_data()
        # expect numeric coords and street parsed
        self.assertAlmostEqual(partner.partner_latitude, -1.234)
        self.assertAlmostEqual(partner.partner_longitude, -78.456)
        self.assertEqual(partner.precision_level, "house")

    def test_action_geolocalize_uses_mapconfig(self):
        partner = self.env["res.partner"].create(
            {"name": "P1", "city": "Quito", "street": "Main St"}
        )

        with patch(
            "odoo.addons.web_map_field.models.map_config.MapPickerConfig.geocode",
            return_value={
                "lat": -1.0,
                "lng": -78.0,
                "boundingbox": None,
            },
        ):
            with patch.object(self.env, "ref", wraps=self.env.ref):
                # call geolocalize
                partner.action_geolocalize()

        # After geolocalize, coordinates should be set (city-level fallback)
        self.assertNotEqual(partner.partner_latitude, 0)
        self.assertNotEqual(partner.partner_longitude, 0)

    def test_onchange_address_geolocalize_integration(self):
        """Integration test for address onchange triggering geolocalize."""
        partner = self.env["res.partner"].new(
            {
                "name": "Test Partner",
                "city": "Guayaquil",
                "street": "Av. 9 de Octubre",
            }
        )

        with patch(
            "odoo.addons.web_map_field.models.map_config.MapPickerConfig.geocode",
            return_value={
                "lat": -2.189,
                "lng": -79.889,
                "boundingbox": None,
            },
        ):
            partner._onchange_address_geolocalize()

        # Check that coordinates are updated
        self.assertAlmostEqual(partner.partner_latitude, -2.189)
        self.assertAlmostEqual(partner.partner_longitude, -79.889)
