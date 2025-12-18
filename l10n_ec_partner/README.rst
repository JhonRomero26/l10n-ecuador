l10n_ec_partner
===============

This module improves partner creation for Ecuadorian companies by auto-populating
partner data based on an Ecuadorian VAT (10 digits for DNI/Cédula, 13 digits for RUC)
using a remote HTTP endpoint.

It also derives geographic fields (province/state, canton, parish, city) from the VAT
prefix when possible.

Configuration
-------------

- Set the System Parameters:

  - ``l10n_ec_partner.api_url``: Base URL for the partner lookup endpoint.
  - ``l10n_ec_partner.api_key``: Optional Bearer token used to authenticate.

This module ships a default value for ``l10n_ec_partner.api_url`` in
``data/ir_config_parameter.xml``.

Usage
-----

For companies whose country is Ecuador (EC):

- When creating a partner, if you type a 10- or 13-digit number in the *Name* field
  (quick-create / Many2one quick creation), the module treats it as the VAT and tries
  to autocomplete.
- When creating/editing a partner, if VAT is a 10- or 13-digit number and Name is empty,
  the module tries to autocomplete.

Technical Notes
---------------

- External dependency: ``requests`` (declared in the manifest).
- The HTTP request uses a short timeout and failures are handled gracefully.

Security Notes
--------------

- The API key is stored in ``ir.config_parameter`` and should be configured only by
  administrators.
- The module reads these parameters server-side (using sudo) to perform the lookup,
  but does not expose the API key in partner fields.

Known Issues / Roadmap
----------------------

- Optionally surface API failures as non-blocking UI warnings.

Credits
-------

Authors
~~~~~~~

- Luis Romero

Maintainers
~~~~~~~~~~~

This module is maintained by Mass (https://mass.ec).
