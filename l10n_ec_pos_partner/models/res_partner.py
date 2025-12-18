import logging

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def create_from_ui(self, partner_data):
        """Create a partner from the POS UI payload.

        Accept either a dict representing a partner (single record) or an
        iterable (list/tuple) with partner dicts -- the POS frontend sends
        an array with a single object in some flows.
        """
        try:
            # Normalize payload that may be an array from the frontend
            if isinstance(partner_data, list | tuple):
                if not partner_data:
                    raise UserError(_("Invalid partner data sent."))
                partner_vals = partner_data[0]
            else:
                partner_vals = partner_data

            # The l10n_ec_partner module should automatically handle the name fetching
            # when a partner is created with a VAT number.
            partner = self.create(partner_vals)
            return partner.id
        except UserError as e:
            _logger.warning("UserError during partner creation from UI: %s", str(e))
            raise e
        except Exception as e:
            _logger.exception("Unexpected error during partner creation from UI")
            base_msg = _("An unexpected error occurred while creating the customer: %s")
            msg = base_msg % (str(e),)
            raise UserError(msg) from e
