from odoo.addons.l10n_ec_account_edi.tests.test_edi_common import TestL10nECEdiCommon


class TestL10nECWithholdCommon(TestL10nECEdiCommon):
    """Base test class for l10n_ec_withhold.

    Extends TestL10nECEdiCommon to ensure that purchase invoices
    always have a default tax support ('01') when none is set,
    which is required by the withholding module.
    """

    def _l10n_ec_create_form_move(
        self,
        move_type,
        internal_type,
        partner,
        taxes=None,
        products=None,
        journal=None,
        latam_document_type=None,
        use_payment_term=False,
        form_id=None,
    ):
        new_move_form = super()._l10n_ec_create_form_move(
            move_type,
            internal_type,
            partner,
            taxes,
            products,
            journal,
            latam_document_type,
            use_payment_term,
            form_id,
        )
        if move_type == "in_invoice" and not new_move_form.l10n_ec_tax_support:
            new_move_form.l10n_ec_tax_support = "01"
        return new_move_form
