L10N EC POS Partner
===================

This small module customizes the Point of Sale partner creation flow for Ecuador
by delegating numeric "name" values (DNI/RUC) to the partner creation logic so
that VAT-based autocompletion can occur.

Configuration
-------------

- None. This module depends on ``l10n_ec_partner`` and reuses its configuration
  (API URL / API key) if present.

Usage
-----

From the POS customer search screen, when the user types a numeric CI/RUC
(10 or 13 digits) and confirms, the module attempts to create the partner
using the numeric value as the name; the partner autocomplete in
``l10n_ec_partner`` will populate the rest of the fields.

Contributors
------------

- Luis Romero (https://mass.ec)

License
-------

LGPL-3
