# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestL10nEcOte(TransactionCase):
    """Test the ecuadorian geopolitical division."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The data is loaded from CSV, so we find the records to test them.
        cls.state_azuay = cls.env.ref("base.state_ec_01")
        cls.canton_cuenca = cls.env.ref("l10n_ec_ote.canton_0101")
        cls.parish_bellavista = cls.env.ref("l10n_ec_ote.parish_010101") # Suffix 01 (<50)
        
        # Another canton and its parishes for testing purposes
        cls.canton_giron = cls.env.ref("l10n_ec_ote.canton_0102") # Giron
        cls.parish_giron_urbana = cls.env.ref("l10n_ec_ote.parish_010250") # Giron (suffix 50)
        cls.parish_giron_rural_asuncion = cls.env.ref("l10n_ec_ote.parish_010251") # Asuncion (suffix 51)

        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
            'country_id': cls.env.ref('base.ec').id,
        })
        # Need to ensure the partner is not linked to any specific location for initial tests
        cls.partner.write({
            'state_id': False,
            'canton_id': False,
            'parish_id': False,
            'city': False,
        })

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
        self.partner.write({
            'state_id': self.state_azuay.id,
            'canton_id': self.canton_cuenca.id,
            'parish_id': self.parish_bellavista.id,
        })
        self.assertEqual(self.partner.state_id, self.state_azuay)
        self.assertEqual(self.partner.canton_id, self.canton_cuenca)
        self.assertEqual(self.partner.parish_id, self.parish_bellavista)

    def test_domain_on_parish(self):
        """Check that parish domain is correctly limited by the canton."""
        # A partner in canton 'Cuenca' should only see parishes from 'Cuenca'.
        partner = self.env['res.partner'].create({
            'name': 'Partner in Cuenca',
            'country_id': self.env.ref('base.ec').id,
            'state_id': self.state_azuay.id,
            'canton_id': self.canton_cuenca.id,
        })

        # In a form view context, the domain on `parish_id` would be something like
        # `[('canton_id', '=', canton_id)]`.
        # We can simulate this by searching with the domain.
        parishes_in_domain = self.env['l10n_ec_ote.parish'].search([
            ('canton_id', '=', partner.canton_id.id)
        ])

        self.assertIn(self.parish_bellavista, parishes_in_domain)

        # Check a parish from another canton is not in the list
        canton_giron = self.env.ref("l10n_ec_ote.canton_0102")
        parish_giron = self.env.ref("l10n_ec_ote.parish_010250")
        self.assertNotIn(parish_giron, parishes_in_domain)
        
    def test_onchange_city_empty_state(self):
        """Test city becomes empty if state is cleared."""
        # Set a state and canton first to have a city value
        self.partner.state_id = self.state_azuay
        self.partner.canton_id = self.canton_cuenca
        self.partner._onchange_location_set_city()
        self.assertEqual(self.partner.city, self.env.ref("l10n_ec_ote.parish_010150").name) # Urban parish for Cuenca

        self.partner.state_id = False
        self.partner._onchange_location_set_city()
        self.assertEqual(self.partner.city, '')

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
        self.partner.parish_id = False # Clear parish first
        self.partner._onchange_location_set_city() # This will set city to canton_cuenca's urban parish name
        
        # Now set parish_bellavista (suffix 01 < 50)
        self.partner.parish_id = self.parish_bellavista
        self.partner._onchange_location_set_city()
        # The city should remain the canton's urban parish name
        self.assertEqual(self.partner.city, self.env.ref("l10n_ec_ote.parish_010150").name)

    def test_onchange_city_canton_only_urban_parish(self):
        """Test city is urban parish name when only canton is set and urban parish exists."""
        # Cuenca has an urban parish (l10n_ec_ote.parish_010150 which is "Cuenca")
        self.partner.state_id = self.state_azuay
        self.partner.canton_id = self.canton_cuenca
        self.partner.parish_id = False # Ensure no parish is set
        self.partner._onchange_location_set_city()
        # The urban parish for Cuenca (canton_0101) is "Cuenca" (parish_010150)
        self.assertEqual(self.partner.city, self.env.ref("l10n_ec_ote.parish_010150").name)

    def test_onchange_city_state_only(self):
        """Test city is first canton name when only state is set."""
        self.partner.state_id = self.state_azuay
        self.partner.canton_id = False
        self.partner.parish_id = False
        self.partner._onchange_location_set_city()
        # The first canton for Azuay (state_ec_01) by code is Cuenca (canton_0101)
        self.assertEqual(self.partner.city, self.canton_cuenca.name)
