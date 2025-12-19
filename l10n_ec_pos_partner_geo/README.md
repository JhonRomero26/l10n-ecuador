# L10n EC POS Partner Geo

## Overview

This Odoo module integrates the map picker widget into the Point of Sale (POS)
application for Ecuador-specific localization. It ensures that the geographic location
picker is available when managing partner information in the POS context.

## Features

- **Map Picker Widget in POS**: Loads the `map_picker` field widget assets into the POS
  bundle
- **Partner Geolocation**: Integrates with the `l10n_ec_partner_geo` module to manage
  partner geographic data
- **Asset Management**: Automatically includes JavaScript, XML templates, and SCSS
  styles from the `web_map_field` module

## Dependencies

- `point_of_sale`: Core Point of Sale module
- `web_map_field`: Map picker widget implementation
- `l10n_ec_partner_geo`: Partner geolocation data for Ecuador

## Installation

1. Ensure all dependencies are installed
2. Install the module through Odoo Apps

## Usage

Once installed, the map picker widget will be available in partner forms when accessed
through the POS interface. Users can:

- Set partner geographic locations using an interactive map
- View latitude and longitude coordinates
- Adjust location precision levels (Street, City, State, Country, etc.)

## Technical Details

### Assets Included

The module loads the following assets from `web_map_field`:

- JavaScript components for map interaction
- XML templates for UI elements
- SCSS stylesheets for styling

### Views

- **res_partner_form_view_inherit_pos_map_picker**: Inherits from
  `l10n_ec_partner_geo.view_partner_form_geolocation_ec` and ensures the `map_picker`
  widget is properly configured in the POS context

## Configuration

No additional configuration is required beyond installing the module. The map picker
widget will automatically be available in partner forms accessed through the POS
application.

## Collaborators

- Luis Romero (https://mass.ec)

## License

This module is licensed under the LGPL-3 license, following the Odoo Community
Association (OCA) standards.

## Support

For issues or questions regarding this module, please refer to the main repository or
contact the development team.
