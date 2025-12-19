# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import json

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    _geo_onchange_cache = {}

    def _geocode_in_city(self, address, city_name, country_codes=None, viewbox=None):
        """Geocode but never accept results outside the selected city."""
        MapConfig = self.env["web.map.config"]
        result = MapConfig.geocode(
            address,
            country_codes=country_codes,
            city_name=city_name,
            viewbox=viewbox,
            bounded=bool(viewbox),
        )
        if not result:
            return None

        if city_name:
            addr = result.get("address") or {}
            if addr:
                result_city = (
                    addr.get("city")
                    or addr.get("town")
                    or addr.get("village")
                    or addr.get("municipality")
                    or ""
                )
                if (
                    result_city
                    and result_city.strip().lower() != city_name.strip().lower()
                ):
                    return None
            else:
                formatted = (result.get("formatted_address") or "").lower()
                if city_name.strip().lower() not in formatted:
                    return None
        return result

    @api.onchange("map_picker_data")
    def _onchange_map_picker_data(self):
        """Update fields when the map JSON changes.

        This allows address and coordinates to refresh in the form without
        saving the record.
        """
        MapConfig = self.env["web.map.config"]
        precision_map = {
            "house": "house",
            "address": "address",
            "building": "district",
            "street": "street",
            "street_number": "address",
            "city": "city",
            "district": "district",
            "state": "state",
            "country": "country",
        }
        for record in self:
            data = record.map_picker_data
            if not data:
                continue
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except (json.JSONDecodeError, TypeError):
                    continue
            lat = data.get("lat") or data.get("latitude")
            lon = data.get("lon") or data.get("longitude")
            if lat is not None:
                record.partner_latitude = float(lat)
            if lon is not None:
                record.partner_longitude = float(lon)
            precision = data.get("precision") or data.get("precision_level")
            if precision:
                mapped_precision = precision_map.get(precision, "exact")
                record.precision_level = mapped_precision
            parsed = MapConfig.parse_map_result(data)
            record_ctx = record.with_context(from_map_picker=True)
            # Update address fields from the parsed map result
            if parsed.get("street"):
                record_ctx.street = parsed["street"]
            if parsed.get("city"):
                record_ctx.city = parsed["city"]
            if parsed.get("zip"):
                record_ctx.zip = parsed["zip"]
            if parsed.get("country"):
                country = self.env["res.country"].search(
                    [
                        "|",
                        ("name", "ilike", parsed["country"]),
                        ("code", "=", parsed["country"]),
                    ],
                    limit=1,
                )
                if country:
                    record_ctx.country_id = country.id
                    if parsed.get("state"):
                        state = self.env["res.country.state"].search(
                            [
                                ("name", "ilike", parsed["state"]),
                                ("country_id", "=", country.id),
                            ],
                            limit=1,
                        )
                        if state:
                            record_ctx.state_id = state.id

    @api.depends("partner_latitude", "partner_longitude", "street", "city")
    def _compute_map_picker_data(self):
        """Prepare the map configuration for the widget."""
        MapConfig = self.env["web.map.config"]

        for record in self:
            record.map_picker_data = {
                "latitude": record.partner_latitude or 0.0,
                "longitude": record.partner_longitude or 0.0,
                "address": ", ".join(filter(None, [record.street, record.city])) or "",
                "precision_level": record.precision_level or "house",
                "precision": record.precision_level or "house",  # For the JS widget
                "use_google": MapConfig.is_google_provider(),
                "google_api_key": MapConfig.get_google_api_key() or "",
            }

    def _inverse_map_picker_data(self):
        """Process the map result and update the fields."""
        MapConfig = self.env["web.map.config"]

        # Mapping of precisions from the widget to the model
        precision_map = {
            "house": "house",
            "address": "address",
            "building": "district",
            "street": "street",
            "street_number": "address",
            "city": "city",
            "district": "district",
            "state": "state",
            "country": "country",
        }

        for record in self:
            data = record.map_picker_data
            if not data:
                continue

            # Parse JSON if it comes as string
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except (json.JSONDecodeError, TypeError):
                    continue

            # Update coordinates (the widget sends lat/lon or latitude/longitude)
            lat = data.get("lat") or data.get("latitude")
            lon = data.get("lon") or data.get("longitude")
            if lat is not None:
                record.partner_latitude = float(lat)
            if lon is not None:
                record.partner_longitude = float(lon)

            # Update precision (map widget values to model values)
            precision = data.get("precision") or data.get("precision_level")
            if precision:
                mapped_precision = precision_map.get(precision, "exact")
                record.precision_level = mapped_precision

            # Process map address using parse_map_result to normalize
            parsed = MapConfig.parse_map_result(data)

            record_ctx = record.with_context(from_map_picker=True)

            # Update address fields directly from parsed
            if parsed.get("street"):
                record_ctx.street = parsed["street"]
            if parsed.get("city"):
                record_ctx.city = parsed["city"]
            if parsed.get("zip"):
                record_ctx.zip = parsed["zip"]

            # Search for country and state
            if parsed.get("country"):
                country = self.env["res.country"].search(
                    [
                        "|",
                        ("name", "ilike", parsed["country"]),
                        ("code", "=", parsed["country"]),
                    ],
                    limit=1,
                )
                if country:
                    record_ctx.country_id = country.id
                    if parsed.get("state"):
                        state = self.env["res.country.state"].search(
                            [
                                ("name", "ilike", parsed["state"]),
                                ("country_id", "=", country.id),
                            ],
                            limit=1,
                        )
                        if state:
                            record_ctx.state_id = state.id

    def action_geolocalize(self):
        """Geolocalize the partner using the address."""
        if self.env.context.get("from_map_picker"):
            return

        MapConfig = self.env["web.map.config"]
        for record in self:
            if record.precision_level == "house":
                continue
            if not record.city:
                continue

            street = (record.street or "").strip()
            city = (record.city or "").strip()

            if street and len(street) < 4:
                continue

            cache_key = (
                city,
                street,
                record.state_id.id or 0,
                record.country_id.id or 0,
            )
            cached = self._geo_onchange_cache.get(cache_key)
            if cached:
                record.partner_latitude = cached["lat"]
                record.partner_longitude = cached["lng"]
                record.precision_level = cached["precision"]
                continue

            country_codes = (
                record.country_id.code.lower()
                if record.country_id and record.country_id.code
                else None
            )

            city_parts = [
                city,
                record.state_id.name if record.state_id else None,
                record.country_id.name if record.country_id else None,
            ]
            city_address = ", ".join(filter(None, city_parts))

            city_result = MapConfig.geocode(
                city_address,
                country_codes=country_codes,
                city_name=city,
            )
            if not city_result:
                continue

            viewbox = (
                city_result.get("boundingbox") if "boundingbox" in city_result else None
            )

            if street:
                street_address = f"{street}, {city_address}"
                result = record._geocode_in_city(
                    street_address,
                    city_name=city,
                    country_codes=country_codes,
                    viewbox=viewbox,
                )
                if result:
                    record.partner_latitude = result.get("lat", 0)
                    record.partner_longitude = result.get("lng", 0)
                    record.precision_level = "street"
                    self._geo_onchange_cache[cache_key] = {
                        "lat": record.partner_latitude,
                        "lng": record.partner_longitude,
                        "precision": record.precision_level,
                    }
                    continue

            record.partner_latitude = city_result.get("lat", 0)
            record.partner_longitude = city_result.get("lng", 0)
            record.precision_level = "city"
            self._geo_onchange_cache[cache_key] = {
                "lat": record.partner_latitude,
                "lng": record.partner_longitude,
                "precision": record.precision_level,
            }

    @api.onchange("street", "city")
    def _onchange_address_geolocalize(self):
        if self.env.context.get("from_map_picker"):
            return
        for record in self:
            if record.precision_level == "house":
                continue
        self.action_geolocalize()
