.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================================
Ecuadorian Geopolitical Division
==================================

This module provides the complete geopolitical division of Ecuador, including provinces, cantons, and parishes. It extends the partner (contact) form to include canton and parish fields, enabling precise address management for Ecuadorian locations. The module automatically sets the city based on selected geopolitical levels and ensures data integrity through validation.

Tested on version
=================
18.0

Installation
============

To install this module, you need to:

1. Ensure the dependencies 'base' and 'l10n_ec' are installed.
2. Install the module via Odoo’s Apps menu or using the command line.
3. The module will automatically load all Ecuadorian geopolitical data (provinces, cantons, parishes) upon installation.

Configuration
=============

No additional configuration is required after installation. The module integrates seamlessly with the existing partner form.

Usage
=====

To use this module:

1. Navigate to the Contacts (Partners) menu in Odoo.
2. Create or edit a partner (customer, supplier, or contact).
3. Select Ecuador as the country.
4. The Canton and Parish fields will appear in the address section.
5. Select the Province (State) first, then the Canton, and optionally the Parish.
6. The City field will be automatically populated based on your selections:

   - If a Parish is selected: The city is set to the parish name for urban parishes (code ending >= 50), otherwise it keeps the canton name.
   - If only a Canton is selected: The city is set to the urban parish name (if available) or the canton name.
   - If only a Province is selected: The city is set to the first canton's name.

7. The module validates selections to ensure cantons belong to the chosen province and parishes to the selected canton.

Functionalitites
================

* **Geopolitical Data Models**: Defines models for Cantons and Parishes, linked to Provinces.
* **Partner Form Extension**: Adds Canton and Parish fields to res.partner with automatic city setting and validation logic.
* **Data Integrity**: Onchange methods ensure hierarchical consistency (Province > Canton > Parish).
* **Localization Defaults**: Automatically sets country to Ecuador and language to Spanish (Ecuador) for partners created by Ecuadorian companies.
* **UI Integration**: Fields are visible only for Ecuadorian partners, with filtered dropdowns.
* **Pre-loaded Data**: Includes CSV files with all official Ecuadorian cantons and parishes.

Demonstration in runbot
=======================

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/212/18.0

Known issues / Roadmap
======================

* There are no known issues.
* The module is complete and operational.

Bug Tracker
===========
Bugs are tracked on `GitHub Issues <https://github.com/OCA/l10n-ecuador/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/l10n-ecuador/issues/new?body=module:%20l10n_ec_ote%0Aversion:%2018.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Fábrica de Software Libre <desarrollo@libre.ec>
* Daniel Alejandro Mendieta <damendieta@gmail.com>
* Luis Romero <lromero@mass.ec>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
