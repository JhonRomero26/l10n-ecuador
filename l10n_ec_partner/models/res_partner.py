try:
    import requests
except ImportError:
    requests = None

import base64
import logging

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _map_api_direct_fields(self, api_data, mapped):
        direct_fields = [
            "name",
            "is_company",
            "company_type",
            "street",
            "street2",
            "city",
            "zip",
            "phone",
            "email",
            "lang",
            "website",
        ]
        for field in direct_fields:
            if field in api_data and api_data[field] is not False:
                mapped[field] = api_data[field]

    def _map_api_image(self, api_data, mapped):
        image_b64 = api_data.get("image")
        if not image_b64:
            return
        if image_b64 is False:
            return
        image_bytes = base64.b64decode(image_b64)
        mapped["image_1920"] = image_bytes

    def _map_api_country(self, api_data, mapped):
        if "country_id" in mapped:
            return

        country_name = api_data.get("country_name")
        if country_name:
            country = self.env["res.country"].search(
                [("name", "=", country_name)], limit=1
            )
            if country:
                mapped["country_id"] = country.id
                return

        ecuador = self.env.ref("base.ec", raise_if_not_found=False)
        if ecuador:
            mapped["country_id"] = ecuador.id

    def _map_api_identification_type(self, api_data, mapped, vat=None):
        if "l10n_latam_identification_type_id" in mapped:
            return

        if vat:
            ident_type = self._l10n_ec_get_identification_type_from_vat(
                vat,
                country_id=mapped.get("country_id"),
            )
            if ident_type:
                mapped["l10n_latam_identification_type_id"] = ident_type.id
                return

        api_ident_name = (api_data.get("identification_type_name") or "").strip()
        if not api_ident_name:
            return

        ident_type = False
        ident_lower = api_ident_name.lower()
        if ident_lower == "ruc":
            ident_type = self.env.ref("l10n_ec.ec_ruc", raise_if_not_found=False)
        elif ident_lower in ("cédula", "cedula", "dni"):
            ident_type = self.env.ref("l10n_ec.ec_dni", raise_if_not_found=False)

        if not ident_type:
            country_id = mapped.get("country_id")
            if not country_id:
                ec = self.env.ref("base.ec", raise_if_not_found=False)
                country_id = ec.id if ec else False
            domain = [("name", "=", api_ident_name)]
            if country_id:
                domain.append(("country_id", "=", country_id))
            ident_type = self.env["l10n_latam.identification.type"].search(
                domain, limit=1
            )

        if ident_type:
            mapped["l10n_latam_identification_type_id"] = ident_type.id

    def _map_api_state(self, api_data, mapped):
        state_name = api_data.get("state_name")
        country_id = mapped.get("country_id")
        if not state_name or not country_id:
            return
        state = self.env["res.country.state"].search(
            [("name", "=", state_name), ("country_id", "=", country_id)], limit=1
        )
        if state:
            mapped["state_id"] = state.id

    def _map_api_canton_parish(self, api_data, mapped):
        canton_name = api_data.get("canton_name")
        if canton_name:
            canton = self.env["l10n_ec_ote.canton"].search(
                [("name", "=", canton_name)], limit=1
            )
            if canton:
                mapped["canton_id"] = canton.id

        parish_name = api_data.get("parish_name")
        if parish_name:
            parish = self.env["l10n_ec_ote.parish"].search(
                [("name", "=", parish_name)], limit=1
            )
            if parish:
                mapped["parish_id"] = parish.id

    def _l10n_ec_get_identification_type_from_vat(self, vat, country_id=None):
        """Return the Ecuadorian identification type for a given VAT.

        We prefer XML IDs (stable across languages) and fall back to a name-based
        search when needed.
        """
        vat = (vat or "").strip()
        if not vat or not vat.isdigit() or len(vat) not in (10, 13):
            return self.env["l10n_latam.identification.type"]

        if len(vat) == 13:
            ident = self.env.ref("l10n_ec.ec_ruc", raise_if_not_found=False)
            if ident:
                return ident
            ident_name = "RUC"
        else:
            ident = self.env.ref("l10n_ec.ec_dni", raise_if_not_found=False)
            if ident:
                return ident
            ident_name = "Cédula"

        if not country_id:
            country_id = self.env.ref("base.ec", raise_if_not_found=False)
            country_id = country_id.id if country_id else False
        domain = [("name", "=", ident_name)]
        if country_id:
            domain.append(("country_id", "=", country_id))
        return self.env["l10n_latam.identification.type"].search(domain, limit=1)

    def _prepare_ec_partner_vals(self, vals):
        """
        This helper encapsulates all the logic for auto-populating partner data
        for Ecuadorian localization. It modifies the 'vals' dictionary in-place.
        """
        if self.env.company.country_id.code != "EC" or self.env.context.get(
            "skip_partner_autocomplete"
        ):
            return

        name = vals.get("name", "")
        vat = vals.get("vat", "")

        # Determine if we need to run autocomplete
        run_autocomplete = False
        if not vat and name and name.isdigit() and len(name) in [10, 13]:
            vals["vat"] = name
            vals["name"] = ""
            run_autocomplete = True
        elif vat and vat.isdigit() and len(vat) in [10, 13] and not name:
            run_autocomplete = True

        if run_autocomplete:
            self._autocomplete_partner_data(vals)

        # Set state and city from VAT if possible
        if vals.get("vat") and not vals.get("state_id"):
            vat_number = vals["vat"]
            if len(vat_number) >= 2 and vat_number.isdigit():
                province_code = vat_number[:2]
                ecuador_country = self.env.ref("base.ec", raise_if_not_found=False)
                if ecuador_country:
                    state = self.env["res.country.state"].search(
                        [
                            ("code", "=", province_code),
                            ("country_id", "=", ecuador_country.id),
                        ],
                        limit=1,
                    )
                    if state:
                        vals["state_id"] = state.id
                        if not vals.get("canton_id"):
                            first_canton = self.env["l10n_ec_ote.canton"].search(
                                [("state_id", "=", state.id)], order="code asc", limit=1
                            )
                            if first_canton:
                                vals["canton_id"] = first_canton.id
                                # Set parish to the urban parish if exists
                                urban_parish = self.env["l10n_ec_ote.parish"].search(
                                    [
                                        ("canton_id", "=", first_canton.id),
                                        ("code", "like", "%50"),
                                    ],
                                    limit=1,
                                )
                                if urban_parish:
                                    vals["parish_id"] = urban_parish.id
                                # Set city to the parish or canton name
                                if not vals.get("city"):
                                    vals["city"] = (
                                        urban_parish.name
                                        if urban_parish
                                        else first_canton.name
                                    )

    @api.model
    def name_create(self, name):
        """
        Override name_create for 'quick create' from a Many2one field.
        If the name looks like a VAT/DNI, run the full autocomplete logic
        and return the real partner name for display.
        """
        if (
            self.env.company.country_id.code == "EC"
            and name.isdigit()
            and len(name) in [10, 13]
            and not self.env.context.get("skip_ec_partner_preparation")
        ):
            vals = {"name": name}
            self._prepare_ec_partner_vals(vals)
            # Pass context to skip preparation in the subsequent 'create' call
            partner = self.with_context(skip_ec_partner_preparation=True).create(
                [vals]
            )[0]
            return partner.id, partner.display_name
        return super().name_create(name)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.context.get("skip_ec_partner_preparation"):
            for vals in vals_list:
                self._prepare_ec_partner_vals(vals)
        return super().create(vals_list)

    def write(self, vals):
        is_company_map = {}
        ident_type_map = {}
        if "vat" in vals and "company_type" not in vals and "is_company" not in vals:
            vat = vals.get("vat") or ""
            for partner in self:
                country_id = vals.get("country_id", partner.country_id.id)
                if not country_id:
                    continue
                if isinstance(country_id, list | tuple):
                    continue
                country = self.env["res.country"].browse(country_id)

                if country.code == "EC" and vat.isdigit():
                    is_company = False
                    if len(vat) == 13 and vat[2] in ["6", "9"]:
                        is_company = True

                    if is_company != partner.is_company:
                        is_company_map[partner.id] = is_company

                    # Set identification type
                    ident_type = self._l10n_ec_get_identification_type_from_vat(
                        vat, country_id=country_id
                    )
                    if (
                        ident_type
                        and ident_type != partner.l10n_latam_identification_type_id
                    ):
                        ident_type_map[partner.id] = ident_type.id

        res = super().write(vals)

        if is_company_map:
            for partner_id, is_company in is_company_map.items():
                self.env["res.partner"].browse(partner_id).is_company = is_company

        if ident_type_map:
            for partner_id, ident_type_id in ident_type_map.items():
                self.env["res.partner"].browse(
                    partner_id
                ).l10n_latam_identification_type_id = ident_type_id

        return res

    @api.onchange("vat", "country_id")
    def _onchange_vat_l10n_ec(self):
        if (
            self.country_id
            and self.country_id.code == "EC"
            and self.vat
            and self.vat.isdigit()
        ):
            is_company = False
            if len(self.vat) == 13 and self.vat[2] in ["6", "9"]:
                is_company = True
            self.is_company = is_company

            # Set identification type
            ident_type = self._l10n_ec_get_identification_type_from_vat(
                self.vat, country_id=self.country_id.id
            )
            if ident_type:
                self.l10n_latam_identification_type_id = ident_type

    @api.onchange("name")
    def _onchange_name_l10n_ec(self):
        if (
            self.env.company.country_id.code == "EC"
            and self.name
            and self.name.isdigit()
            and len(self.name) in [10, 13]
            and not self.env.context.get("skip_partner_autocomplete")
        ):
            # Build a vals dict to reuse the existing create logic.
            vals = {"name": self.name}
            self._prepare_ec_partner_vals(vals)
            # Apply changes back to the record.
            for key, value in vals.items():
                if key != "name" or value:  # Only overwrite name if it changed.
                    setattr(self, key, value)

    def _autocomplete_partner_data(self, vals):
        vat = vals.get("vat")
        if not vat or not vat.isdigit() or len(vat) not in [10, 13]:
            return

        api_url = (
            self.env["ir.config_parameter"].sudo().get_param("l10n_ec_partner.api_url")
        )
        api_key = (
            self.env["ir.config_parameter"].sudo().get_param("l10n_ec_partner.api_key")
        )
        if not api_url:
            _logger.warning("API URL not configured for l10n_ec_partner")
            return

        url = f"{api_url}/{vat}"
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        _logger.info(
            "Attempting to autocomplete partner data for VAT %s from URL %s", vat, url
        )
        try:
            # TODO: Handle errors with UI warnings without breaking the flow.

            response = self._make_request(url, headers=headers)
            if response:
                data = response.json()
                if "error" not in data:
                    _logger.info("Successfully received data for VAT %s", vat)
                    mapped_data = self._map_api_data_to_partner_vals(data, vat)
                    vals.update(mapped_data)
                else:
                    _logger.info(
                        f'API returned error for VAT {vat}: {data.get("error")}'
                    )
            else:
                _logger.warning(f"Failed to get response from API for VAT {vat}")
        except Exception as e:
            _logger.error(f"Exception during API call for VAT {vat}: {str(e)}")

    def _map_api_data_to_partner_vals(self, api_data, vat=None):
        """
        Map the API response data to Odoo res.partner vals dictionary.
        The API returns a generic standard, so we need to convert it to Odoo fields.
        """
        mapped = {}
        self._map_api_direct_fields(api_data, mapped)
        self._map_api_image(api_data, mapped)
        self._map_api_country(api_data, mapped)
        self._map_api_identification_type(api_data, mapped, vat=vat)
        self._map_api_state(api_data, mapped)
        self._map_api_canton_parish(api_data, mapped)
        return mapped

    def _make_request(self, url, headers=None):
        if not requests:
            raise UserError(_("The 'requests' library is not installed."))
        try:
            response = requests.get(url, headers=headers or {}, timeout=5)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException:
            return None
