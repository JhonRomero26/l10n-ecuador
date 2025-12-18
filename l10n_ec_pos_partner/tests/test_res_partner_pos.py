from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestL10nEcPosPartner(TransactionCase):
    def setUp(self):
        super().setUp()
        self.env.company.sudo().write({"country_id": self.env.ref("base.ec").id})

    def test_create_from_ui_accepts_array_and_creates_partner(self):
        def fake_create(self_obj, vals):
            # Create the partner directly without invoking the patched create to
            # avoid recursion and external calls.
            partner_id = self.env["res.partner"]._create(vals)
            return self.env["res.partner"].browse(partner_id)

        # Call create_from_ui while skipping the autocomplete to avoid external
        # HTTP calls and side effects in unit tests.
        partner_id = (
            self.env["res.partner"]
            .with_context(skip_partner_autocomplete=True)
            .create_from_ui([{"name": "1718137159"}])
        )

        partner = self.env["res.partner"].browse(partner_id)
        self.assertEqual(partner.name, "1718137159")
