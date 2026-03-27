# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestL10nEcOte(TransactionCase):
    """Test the ecuadorian geopolitical division."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The data is loaded from CSV, so we find the records to test them.
        cls.state_azuay = cls.env.ref("base.state_ec_01")
        cls.state_loja = cls.env.ref("base.state_ec_11")
        cls.canton_cuenca = cls.env.ref("l10n_ec_ote.canton_0101")
        cls.canton_pindal = cls.env.ref("l10n_ec_ote.canton_1114")
        # Suffix 01 (<50)
        cls.parish_bellavista = cls.env.ref("l10n_ec_ote.parish_010101")

        # Another canton and its parishes for testing purposes
        cls.canton_giron = cls.env.ref("l10n_ec_ote.canton_0102")  # Giron
        cls.parish_giron_urbana = cls.env.ref(
            "l10n_ec_ote.parish_010250"
        )  # Giron (suffix 50)
        cls.parish_giron_rural_asuncion = cls.env.ref(
            "l10n_ec_ote.parish_010251"
        )  # Asuncion (suffix 51)

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "country_id": cls.env.ref("base.ec").id,
            }
        )
        # For initial tests
        cls.partner.write(
            {
                "state_id": False,
                "canton_id": False,
                "parish_id": False,
                "city": False,
            }
        )

    def test_canton_data_is_loaded(self):
        """Test that a sample canton from CSV is loaded correctly."""
        self.assertEqual(self.canton_cuenca.name, "Cuenca")
        self.assertEqual(self.canton_cuenca.code, "0101")
        self.assertEqual(self.canton_cuenca.state_id, self.state_azuay)

    def test_parish_data_is_loaded(self):
        """Test that a sample parish from CSV is loaded correctly."""
        self.assertEqual(self.parish_bellavista.name, "Bellavista")
        self.assertEqual(self.parish_bellavista.code, "010101")
        self.assertEqual(self.parish_bellavista.canton_id, self.canton_cuenca)

    def test_relationships(self):
        """Test the relationships between state, canton, and parish."""
        # Ensure the canton has its parishes
        self.assertIn(self.parish_bellavista, self.canton_cuenca.parish_ids)
        # Ensure the state has its cantons
        self.assertIn(self.canton_cuenca, self.state_azuay.canton_ids)

    def test_partner_fields_assignment(self):
        """Test assigning canton and parish to a partner."""
        self.partner.write(
            {
                "state_id": self.state_azuay.id,
                "canton_id": self.canton_cuenca.id,
                "parish_id": self.parish_bellavista.id,
            }
        )
        self.assertEqual(self.partner.state_id, self.state_azuay)
        self.assertEqual(self.partner.canton_id, self.canton_cuenca)
        self.assertEqual(self.partner.parish_id, self.parish_bellavista)

    def test_domain_on_parish(self):
        """Check that parish domain is correctly limited by the canton."""
        # A partner in canton 'Cuenca' should only see parishes from 'Cuenca'.
        partner = self.env["res.partner"].create(
            {
                "name": "Partner in Cuenca",
                "country_id": self.env.ref("base.ec").id,
                "state_id": self.state_azuay.id,
                "canton_id": self.canton_cuenca.id,
            }
        )

        # In a form view context, the domain on `parish_id` would be something like
        # `[('canton_id', '=', canton_id)]`.
        # We can simulate this by searching with the domain.
        parishes_in_domain = self.env["l10n_ec_ote.parish"].search(
            [("canton_id", "=", partner.canton_id.id)]
        )

        self.assertIn(self.parish_bellavista, parishes_in_domain)

        # Check a parish from another canton is not in the list
        parish_giron = self.env.ref("l10n_ec_ote.parish_010250")
        self.assertNotIn(parish_giron, parishes_in_domain)

    def test_onchange_city_empty_state(self):
        """Test city becomes empty if state is cleared."""
        # Set a state and canton first to have a city value
        self.partner.state_id = self.state_azuay
        self.partner.canton_id = self.canton_cuenca
        self.partner._onchange_location_set_city()
        # Urban parish for Cuenca
        self.assertEqual(
            self.partner.city, self.env.ref("l10n_ec_ote.parish_010150").name
        )

        self.partner.state_id = False
        self.partner._onchange_location_set_city()
        self.assertEqual(self.partner.city, "")

    def test_onchange_city_parish_suffix_ge_50(self):
        """Test city is parish name when parish code suffix >= 50."""
        # Using canton_giron and parish_giron_urbana (code ends in 50)
        self.partner.state_id = self.state_azuay
        self.partner.canton_id = self.canton_giron
        self.partner.parish_id = self.parish_giron_urbana
        self.partner._onchange_location_set_city()
        self.assertEqual(self.partner.city, self.parish_giron_urbana.name)

        # Using parish_giron_rural_asuncion (code ends in 51)
        self.partner.parish_id = self.parish_giron_rural_asuncion
        self.partner._onchange_location_set_city()
        self.assertEqual(self.partner.city, self.parish_giron_rural_asuncion.name)

    def test_onchange_city_parish_suffix_lt_50(self):
        """Test city is canton name when parish code suffix < 50."""
        # Set canton to Cuenca first to have its name as the expected city
        self.partner.state_id = self.state_azuay
        self.partner.canton_id = self.canton_cuenca
        # Clear parish first
        self.partner.parish_id = False
        # This will set city to canton_cuenca's urban parish name
        self.partner._onchange_location_set_city()

        # Now set parish_bellavista (suffix 01 < 50)
        self.partner.parish_id = self.parish_bellavista
        self.partner._onchange_location_set_city()
        # The city should remain the canton's urban parish name
        self.assertEqual(
            self.partner.city, self.env.ref("l10n_ec_ote.parish_010150").name
        )

    def test_onchange_city_canton_only_urban_parish(self):
        """Test city is urban parish name when only canton is set
        and urban parish exists."""
        # Cuenca has an urban parish (l10n_ec_ote.parish_010150 which is "Cuenca")
        self.partner.state_id = self.state_azuay
        self.partner.canton_id = self.canton_cuenca
        self.partner.parish_id = False  # Ensure no parish is set
        self.partner._onchange_location_set_city()
        # The urban parish for Cuenca (canton_0101) is "Cuenca" (parish_010150)
        self.assertEqual(
            self.partner.city, self.env.ref("l10n_ec_ote.parish_010150").name
        )

    def test_onchange_city_state_only(self):
        """Test city is first canton name when only state is set."""
        self.partner.state_id = self.state_azuay
        self.partner.canton_id = False
        self.partner.parish_id = False
        self.partner._onchange_location_set_city()
        # The first canton for Azuay (state_ec_01) by code is Cuenca (canton_0101)
        self.assertEqual(self.partner.city, self.canton_cuenca.name)

    def test_create_partner_defaults_country_and_lang(self):
        """Creating a partner without country/lang uses company's EC defaults."""
        # Ensure company country code is EC
        self.env.company.country_id = self.env.ref("base.ec")

        partner = self.env["res.partner"].create({"name": "Partner Default"})
        self.assertEqual(partner.country_id, self.env.ref("base.ec"))
        self.assertEqual(partner.lang, "es_EC")

        # Even explicit False for country should fallback to the company default
        partner2 = self.env["res.partner"].create(
            {"name": "Partner False", "country_id": False}
        )
        self.assertEqual(partner2.country_id, self.env.ref("base.ec"))

    def test_canton_next_code_for_state(self):
        """The next canton code follows the province sequence."""
        next_code = self.env["l10n_ec_ote.canton"]._get_next_code(self.state_loja)
        self.assertEqual(next_code, "1117")

    def test_canton_wizard_creates_next_code(self):
        """The canton wizard creates a canton with Ecuador defaults."""
        wizard = self.env["l10n_ec_ote.canton.wizard"].create(
            {
                "state_id": self.state_loja.id,
                "name": "Nuevo Cantón",
            }
        )

        self.assertEqual(wizard.country_id, self.env.ref("base.ec"))
        self.assertEqual(wizard.code, "1117")

        action = wizard.action_create_canton()
        canton = self.env["l10n_ec_ote.canton"].browse(action["res_id"])

        self.assertTrue(canton.exists())
        self.assertEqual(canton.state_id, self.state_loja)
        self.assertEqual(canton.code, "1117")
        self.assertEqual(canton.name, "Nuevo Cantón")

    def test_parish_next_code_for_urban_and_rural(self):
        """The parish helper separates urban and rural suffixes."""
        parish_model = self.env["l10n_ec_ote.parish"]
        self.assertEqual(
            parish_model._get_next_code(self.canton_pindal, "urban"), "111401"
        )
        self.assertEqual(
            parish_model._get_next_code(self.canton_pindal, "rural"), "111454"
        )

    def test_parish_wizard_creates_rural_code(self):
        """The parish wizard creates the next rural parish code."""
        wizard = self.env["l10n_ec_ote.parish.wizard"].create(
            {
                "state_id": self.state_loja.id,
                "canton_id": self.canton_pindal.id,
                "parish_type": "rural",
                "name": "Nueva Rural",
            }
        )

        self.assertEqual(wizard.country_id, self.env.ref("base.ec"))
        self.assertEqual(wizard.code, "111454")

        action = wizard.action_create_parish()
        parish = self.env["l10n_ec_ote.parish"].browse(action["res_id"])

        self.assertTrue(parish.exists())
        self.assertEqual(parish.canton_id, self.canton_pindal)
        self.assertEqual(parish.code, "111454")
        self.assertEqual(parish.name, "Nueva Rural")

    def test_parish_wizard_creates_urban_code(self):
        """The parish wizard creates the next urban parish code."""
        wizard = self.env["l10n_ec_ote.parish.wizard"].create(
            {
                "state_id": self.state_loja.id,
                "canton_id": self.canton_pindal.id,
                "parish_type": "urban",
                "name": "Nueva Urbana",
            }
        )

        self.assertEqual(wizard.code, "111401")

        action = wizard.action_create_parish()
        parish = self.env["l10n_ec_ote.parish"].browse(action["res_id"])

        self.assertTrue(parish.exists())
        self.assertEqual(parish.canton_id, self.canton_pindal)
        self.assertEqual(parish.code, "111401")
        self.assertEqual(parish.name, "Nueva Urbana")

    def test_canton_code_prefix_validation(self):
        """Cantons must use the selected province code as prefix."""
        with self.assertRaises(ValidationError):
            self.env["l10n_ec_ote.canton"].create(
                {
                    "state_id": self.state_loja.id,
                    "name": "Cantón Inválido",
                    "code": "0199",
                }
            )

    def test_parish_code_prefix_validation(self):
        """Parishes must use the selected canton code as prefix."""
        with self.assertRaises(ValidationError):
            self.env["l10n_ec_ote.parish"].create(
                {
                    "canton_id": self.canton_pindal.id,
                    "name": "Parroquia Inválida",
                    "code": "119901",
                }
            )

    def test_canton_create_assigns_next_code_without_wizard(self):
        """Direct canton creation still auto-assigns the next code."""
        canton = self.env["l10n_ec_ote.canton"].create(
            {
                "state_id": self.state_loja.id,
                "name": "Cantón Directo",
            }
        )

        self.assertEqual(canton.code, "1117")

    def test_parish_create_assigns_next_code_from_context(self):
        """Direct parish creation uses the parish type from context."""
        parish = (
            self.env["l10n_ec_ote.parish"]
            .with_context(l10n_ec_ote_parish_type="urban")
            .create(
                {
                    "canton_id": self.canton_pindal.id,
                    "name": "Parroquia Directa",
                }
            )
        )

        self.assertEqual(parish.code, "111401")

    def test_parish_invalid_type_raises(self):
        """Only urban and rural parish types are accepted."""
        with self.assertRaises(ValidationError):
            self.env["l10n_ec_ote.parish"]._get_next_code(self.canton_pindal, "other")

    def test_parish_wizard_syncs_state_from_canton(self):
        """Selecting a canton updates the wizard province."""
        wizard = self.env["l10n_ec_ote.parish.wizard"].new(
            {
                "state_id": self.state_azuay.id,
                "canton_id": self.canton_pindal.id,
                "parish_type": "rural",
                "name": "Nueva Rural",
            }
        )

        wizard._onchange_canton_id()

        self.assertEqual(wizard.state_id, self.state_loja)

    def test_parish_wizard_rejects_mismatched_state(self):
        """Wizard validation rejects cantons outside the selected province."""
        with self.assertRaises(ValidationError):
            self.env["l10n_ec_ote.parish.wizard"].create(
                {
                    "state_id": self.state_azuay.id,
                    "canton_id": self.canton_pindal.id,
                    "parish_type": "rural",
                    "name": "Nueva Rural",
                }
            )
