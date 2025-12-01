import logging
import subprocess
from base64 import b64decode
from random import randrange
from tempfile import NamedTemporaryFile

import xmlsig  # pylint: disable=W7936
from cryptography import x509 as crypto_x509  # pylint: disable=W7936
from cryptography.hazmat.primitives import serialization  # pylint: disable=W7936
from cryptography.hazmat.primitives.serialization import pkcs12  # pylint: disable=W7936
from cryptography.x509 import ExtensionNotFound  # pylint: disable=W7936
from cryptography.x509.oid import ExtensionOID, NameOID  # pylint: disable=W7936
from lxml import etree
from xades import XAdESContext, template  # pylint: disable=W7936
from xades.policy import ImpliedPolicy  # pylint: disable=W7936

from odoo import api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

# Commands to extract key and certificate from PKCS#12
# using OpenSSL with legacy support
# The -legacy flag is required for certificates using
# older algorithms (e.g., BCE certificates)
KEY_TO_PEM_CMD = (
    "openssl pkcs12 -nocerts -in %s -out %s -legacy -passin pass:%s -passout pass:%s"
)
CERT_TO_PEM_CMD = (
    "openssl pkcs12 -clcerts -nokeys -in %s -out %s -legacy -passin pass:%s"
)


def convert_key_cer_to_pem(key, password):
    """
    Convert PKCS#12 key to PEM format using OpenSSL command.

    This function uses the OpenSSL command-line tool with the -legacy flag
    to support certificates that use older encryption algorithms (such as
    those from BCE - Banco Central del Ecuador).

    Args:
        key: Binary content of the PKCS#12 file
        password: Password for the PKCS#12 file

    Returns:
        str: Private key in PEM format
    """
    with (
        NamedTemporaryFile(
            "wb", suffix=".p12", prefix="edi.ec.tmp.", delete=False
        ) as p12_file,
        NamedTemporaryFile(
            "r", suffix=".pem", prefix="edi.ec.tmp.", delete=False
        ) as pem_file,
    ):
        p12_file.write(key)
        p12_file.flush()
        command = KEY_TO_PEM_CMD % (p12_file.name, pem_file.name, password, password)
        subprocess.call(command.split())
        pem_file.seek(0)
        key_pem = pem_file.read()
    return key_pem


def convert_cert_to_pem(p12_content, password):
    """
    Extract certificate from PKCS#12 to PEM format using OpenSSL command.

    Args:
        p12_content: Binary content of the PKCS#12 file
        password: Password for the PKCS#12 file

    Returns:
        str: Certificate in PEM format
    """
    with (
        NamedTemporaryFile(
            "wb", suffix=".p12", prefix="edi.ec.tmp.", delete=False
        ) as p12_file,
        NamedTemporaryFile(
            "r", suffix=".pem", prefix="edi.ec.tmp.", delete=False
        ) as pem_file,
    ):
        p12_file.write(p12_content)
        p12_file.flush()
        command = CERT_TO_PEM_CMD % (p12_file.name, pem_file.name, password)
        subprocess.call(command.split())
        pem_file.seek(0)
        cert_pem = pem_file.read()
    return cert_pem


class SriKeyType(models.Model):
    _name = "sri.key.type"
    _description = "Type of electronic key"

    name = fields.Char(size=255, required=True, readonly=False)
    file_content = fields.Binary(string="Signature File")
    file_name = fields.Char(string="Filename", readonly=True)
    password = fields.Char(string="Signing key")
    active = fields.Boolean(string="Active?", default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    state = fields.Selection(
        [
            ("unverified", "Unverified"),
            ("valid", "Valid Signature"),
            ("expired", "Signature Expired"),
        ],
        default="unverified",
        readonly=True,
    )
    # datos informativos del certificado
    issue_date = fields.Date(string="Date of issue", readonly=True)
    expire_date = fields.Date(string="Expiration date", readonly=True)
    subject_serial_number = fields.Char(string="Serial Number (Subject)", readonly=True)
    subject_common_name = fields.Char(string="Organization (Subject)", readonly=True)
    issuer_common_name = fields.Char(string="Organization (Issuer)", readonly=True)
    cert_serial_number = fields.Char(
        string="Serial number (certificate)", readonly=True
    )
    cert_version = fields.Char(string="Version", readonly=True)
    days_for_notification = fields.Integer(string="Days for notification", default=30)

    @tools.ormcache("self.id", "self.write_date", "self.password")
    def _decode_certificate(self):
        """
        Decode PKCS#12 certificate and extract private key and certificates.

        This method first attempts to load the certificate using the cryptography
        library. If that fails (e.g., for certificates using legacy algorithms like
        those from BCE - Banco Central del Ecuador), it falls back to using OpenSSL
        with the -legacy flag.

        Returns:
            tuple: (private_key, certificate, other_certificates)

        Raises:
            UserError: If the certificate cannot be loaded or is invalid.
        """
        self.ensure_one()
        if not self.file_content or not self.password:
            raise UserError(_("Certificate/password not provided."))

        file_content = b64decode(self.file_content)
        password_bytes = self.password.encode("utf-8")
        private_key = None
        cert = None
        other_certs = None

        # First, try to load using cryptography library (modern certificates)
        try:
            private_key, cert, other_certs = pkcs12.load_key_and_certificates(
                file_content, password_bytes
            )
        except Exception as ex:
            _logger.warning(
                "PKCS#12 load with cryptography failed, trying OpenSSL legacy: %s", ex
            )
            try:
                private_key, cert, other_certs = self._decode_certificate_legacy(
                    file_content, password_bytes
                )
            except Exception as legacy_ex:
                _logger.error("Both cryptography and OpenSSL legacy load failed")
                raise UserError(
                    _(
                        "Error opening the signature. Wrong password or "
                        "unsupported file.\n"
                        "Cryptography error: %(crypto_error)s\n"
                        "OpenSSL legacy error: %(openssl_error)s"
                    )
                    % {"crypto_error": str(ex), "openssl_error": str(legacy_ex)}
                ) from None

        if private_key is None or cert is None:
            raise UserError(
                _("PKCS#12 does not contain a private key and end-entity certificate.")
            )

        def has_digital_signature(x509):
            try:
                ku = x509.extensions.get_extension_for_oid(ExtensionOID.KEY_USAGE).value
                return bool(getattr(ku, "digital_signature", False))
            except ExtensionNotFound:
                return True

        if not has_digital_signature(cert) and other_certs:
            for other in other_certs:
                if has_digital_signature(other):
                    cert = other
                    break

        return (private_key, cert, other_certs or [])

    def _decode_certificate_legacy(self, file_content, password_bytes):
        """
        Decode PKCS#12 certificate using OpenSSL command with -legacy flag.

        This method is used as a fallback for certificates that use older
        encryption algorithms not supported by the cryptography library
        (e.g., BCE certificates from Banco Central del Ecuador).

        Args:
            file_content: Binary content of the PKCS#12 file
            password_bytes: Password as bytes

        Returns:
            tuple: (private_key, certificate, other_certificates)
        """
        password = password_bytes.decode("utf-8")

        # Extract private key using OpenSSL with -legacy flag
        private_key_str = convert_key_cer_to_pem(file_content, password)

        # When the file has multiple electronic signatures,
        # it comes with several sections with BEGIN ENCRYPTED PRIVATE KEY
        # differentiated by:
        # * Decryption Key
        # * Signing Key
        # so take from Signing Key if it exists
        start_index = private_key_str.find("Signing Key")
        if start_index >= 0:
            private_key_str = private_key_str[start_index:]

        start_index = private_key_str.find("-----BEGIN ENCRYPTED PRIVATE KEY-----")
        if start_index < 0:
            raise UserError(_("Could not find private key in certificate."))

        private_key_str = private_key_str[start_index:]
        private_key = serialization.load_pem_private_key(
            private_key_str.encode(),
            password_bytes,
        )

        # Extract certificate using OpenSSL with -legacy flag
        cert_pem_str = convert_cert_to_pem(file_content, password)

        # Find the certificate in PEM format
        start_index = cert_pem_str.find("-----BEGIN CERTIFICATE-----")
        if start_index < 0:
            raise UserError(_("Could not find certificate in file."))

        cert_pem_str = cert_pem_str[start_index:]
        cert = crypto_x509.load_pem_x509_certificate(cert_pem_str.encode())

        # For legacy method, we don't extract additional certificates
        # as they are typically not needed for signing
        other_certs = []

        return (private_key, cert, other_certs)

    def action_validate_and_load(self):
        decoded = self._decode_certificate()
        cert = decoded[1]

        issuer = cert.issuer
        subject = cert.subject

        def _attr(name_oid, xname):
            vals = xname.get_attributes_for_oid(name_oid)
            return vals[0].value if vals else ""

        subject_common_name = _attr(NameOID.COMMON_NAME, subject)
        subject_serial_number = _attr(NameOID.SERIAL_NUMBER, subject)
        issuer_common_name = _attr(NameOID.COMMON_NAME, issuer)

        vals = {
            "issue_date": fields.Datetime.context_timestamp(
                self, cert.not_valid_before
            ).date(),
            "expire_date": fields.Datetime.context_timestamp(
                self, cert.not_valid_after
            ).date(),
            "subject_common_name": subject_common_name,
            "subject_serial_number": subject_serial_number,
            "issuer_common_name": issuer_common_name,
            "cert_serial_number": cert.serial_number,
            "cert_version": str(cert.version),  # evita objetos Enum directos
            "state": "valid",
        }
        self.write(vals)
        return True

    def action_sign(self, xml_string_data):
        def new_range():
            return randrange(100000, 999999)

        p12 = self._decode_certificate()
        doc = etree.fromstring(xml_string_data)
        signature_id = f"Signature{new_range()}"
        signature_property_id = f"{signature_id}-SignedPropertiesID{new_range()}"
        certificate_id = f"Certificate{new_range()}"
        reference_uri = f"Reference-ID-{new_range()}"
        signature = xmlsig.template.create(
            xmlsig.constants.TransformInclC14N,
            xmlsig.constants.TransformRsaSha1,
            signature_id,
        )
        xmlsig.template.add_reference(
            signature,
            xmlsig.constants.TransformSha1,
            name=f"SignedPropertiesID{new_range()}",
            uri=f"#{signature_property_id}",
            uri_type="http://uri.etsi.org/01903#SignedProperties",
        )
        xmlsig.template.add_reference(
            signature, xmlsig.constants.TransformSha1, uri=f"#{certificate_id}"
        )
        ref = xmlsig.template.add_reference(
            signature,
            xmlsig.constants.TransformSha1,
            name=reference_uri,
            uri="#comprobante",
        )
        xmlsig.template.add_transform(ref, xmlsig.constants.TransformEnveloped)
        ki = xmlsig.template.ensure_key_info(signature, name=certificate_id)
        data = xmlsig.template.add_x509_data(ki)
        xmlsig.template.x509_data_add_certificate(data)
        xmlsig.template.add_key_value(ki)
        qualifying = template.create_qualifying_properties(signature, name=signature_id)
        props = template.create_signed_properties(
            qualifying, name=signature_property_id
        )
        signed_do = template.ensure_signed_data_object_properties(props)
        template.add_data_object_format(
            signed_do,
            f"#{reference_uri}",
            description="contenido comprobante",
            mime_type="text/xml",
        )
        doc.append(signature)
        ctx = XAdESContext(ImpliedPolicy(xmlsig.constants.TransformSha1))
        ctx.load_pkcs12(p12)
        ctx.sign(signature)
        ctx.verify(signature)
        return etree.tostring(doc, encoding="UTF-8", pretty_print=True).decode()

    def days_to_expire(self):
        if self.expire_date:
            return (self.expire_date - fields.Date.context_today(self)).days
        return 0

    @api.model
    def action_email_notification(self):
        email_template = self.env.ref(
            "l10n_ec_account_edi.email_template_notify", False
        )
        all_companies = self.env["res.company"].search([])
        for company in all_companies:
            certificates = self.search(
                [("company_id", "=", company.id), ("state", "=", "valid")]
            )
            for cert in certificates:
                if 0 < cert.days_to_expire() <= cert.days_for_notification:
                    email_template.send_mail(
                        cert.id, email_layout_xmlid="mail.mail_notification_light"
                    )
        return True
