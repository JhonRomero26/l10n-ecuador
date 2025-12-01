from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import tagged

from .test_edi_common import TestL10nECEdiCommon


@tagged("post_install_l10n", "post_install", "-at_install")
class TestL10nECKeyType(TestL10nECEdiCommon):
    def test_l10n_ec_load_key_type(self):
        # Validar la firma correcta, e informar la fecha de expiración
        self.certificate.action_validate_and_load()
        self.assertEqual(self.certificate.state, "valid")

    def test_invalid_key_type(self):
        # Validar la firma con contraseña equivocada
        self.certificate.password = "invalid"
        with self.assertRaises(UserError):
            with self.assertLogs("odoo.addons.l10n_ec_account_edi"):
                self.certificate.action_validate_and_load()

    def test_l10n_ec_load_key_type_legacy_fallback(self):
        """Test that legacy OpenSSL fallback is used when cryptography fails.

        This simulates the behavior for BCE certificates that use older
        encryption algorithms not supported by the cryptography library.
        """
        # Create a mock that returns the same data as the legacy method would
        with patch(
            "odoo.addons.l10n_ec_account_edi.models.sri_key_type.pkcs12.load_key_and_certificates"
        ) as mock_crypto:
            # Make cryptography fail
            mock_crypto.side_effect = ValueError(
                "Could not deserialize key data. The data may be in an incorrect "
                "format, it may be encrypted with an unsupported algorithm."
            )

            # Clear the cache to ensure fresh execution
            self.certificate.invalidate_recordset()
            self.certificate.env.registry.clear_cache()

            # The certificate should still load using the OpenSSL legacy fallback
            with self.assertLogs(
                "odoo.addons.l10n_ec_account_edi.models.sri_key_type", level="WARNING"
            ) as log:
                self.certificate.action_validate_and_load()

            # Verify the warning about fallback was logged
            self.assertTrue(
                any("trying OpenSSL legacy" in msg for msg in log.output),
                "Expected warning about OpenSSL legacy fallback",
            )
            self.assertEqual(self.certificate.state, "valid")

    def test_l10n_ec_load_key_type_both_methods_fail(self):
        """Test error when both cryptography and OpenSSL legacy fail."""
        # Mock both methods to fail
        with (
            patch(
                "odoo.addons.l10n_ec_account_edi.models.sri_key_type.pkcs12.load_key_and_certificates"
            ) as mock_crypto,
            patch(
                "odoo.addons.l10n_ec_account_edi.models.sri_key_type.SriKeyType._decode_certificate_legacy"
            ) as mock_legacy,
        ):
            mock_crypto.side_effect = ValueError("Cryptography error")
            mock_legacy.side_effect = ValueError("OpenSSL legacy error")

            with self.assertRaises(UserError) as context:
                with self.assertLogs("odoo.addons.l10n_ec_account_edi"):
                    self.certificate.action_validate_and_load()

            # Verify both errors are reported
            error_message = str(context.exception)
            self.assertIn("Cryptography error", error_message)
            self.assertIn("OpenSSL legacy error", error_message)

    def test_l10n_ec_certificate_without_password(self):
        """Test error when certificate or password is missing."""
        self.certificate.password = False
        with self.assertRaises(UserError) as context:
            self.certificate.action_validate_and_load()

        self.assertIn("Certificate/password not provided", str(context.exception))

    def test_l10n_ec_certificate_without_file(self):
        """Test error when certificate file is missing."""
        self.certificate.file_content = False
        with self.assertRaises(UserError) as context:
            self.certificate.action_validate_and_load()

        self.assertIn("Certificate/password not provided", str(context.exception))
