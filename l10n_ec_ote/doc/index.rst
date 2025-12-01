..
   Part of Odoo. See LICENSE file for full copyright and licensing details.

==================================
Ecuadorian Geopolitical Division
==================================

This module provides the geopolitical division of Ecuador, including provinces, cantons, and parishes. It extends the partner (contact) form to include canton and parish fields, allowing for more precise address management in Ecuador. The module also includes logic to automatically set the city based on the selected parish or canton.

Configuration
=============

To configure this module, you need to:

1. Install the module in your Odoo instance. It depends on the 'base' and 'l10n_ec' modules.

2. The module automatically loads data for all Ecuadorian provinces, cantons, and parishes upon installation.

3. No additional configuration is required, as the data is pre-loaded and the fields are integrated into the partner form.

Usage
=====

To use this module, you need to:

* Navigate to the Contacts (Partners) menu in Odoo.

* When creating or editing a partner (customer, supplier, or contact), select Ecuador as the country.

* The Canton and Parish fields will become visible in the address section.

* Select the appropriate Province (State), then Canton, and optionally Parish.

* The City field will be automatically populated based on the selected Parish or Canton, following Ecuadorian geopolitical rules:

  - If a Parish is selected, the city is set to the parish name if its code ends with a suffix >= 50 (urban parishes), otherwise it retains the canton name.

  - If only a Canton is selected, the city is set to the name of the urban parish (code ending in '50') or the canton name if no urban parish exists.

  - If only a Province is selected, the city is set to the name of the first canton in that province.

* The module ensures data integrity by validating that selected cantons belong to the chosen province and parishes belong to the selected canton.

Functionalities
===============

* **Geopolitical Data Models**: Defines models for Cantons and Parishes, linked to Provinces (res.country.state).

* **Partner Extension**: Adds Canton and Parish fields to res.partner, with onchange logic for automatic city setting and validation.

* **Data Loading**: Includes CSV files with all Ecuadorian cantons and parishes data.

* **UI Integration**: Modifies the partner form to display canton and parish fields only for Ecuadorian partners, with appropriate domains and contexts.

* **Address Format**: Updates the address format for Ecuador to include geopolitical divisions.

* **Localization Support**: Defaults country to Ecuador and language to Spanish (Ecuador) for partners created by Ecuadorian companies.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/l10n-ecuador/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed
feedback.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
-------

* OCA

Contributors
------------

* `Luis Romero. <https://github.com/lojanet>`_

Maintainers
-----------

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/l10n-ecuador <https://github.com/OCA/l10n-ecuador/tree/18.0/l10n_ec_ote>`_ project on GitHub.

You are welcome to contribute. To do so, please visit https://odoo-community.org/page/Contribute.
