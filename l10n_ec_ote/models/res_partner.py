from odoo import models, fields, api, _

class ResPartner(models.Model):
    _description = 'Add Canton and Parish fields to partner'
    _inherit = 'res.partner'

    partner_country_code = fields.Char(
        related='country_id.code',
        string="Partner Country Code",
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        # Logic for dynamic default value.
        company = self.env.company
        if company.country_id and company.country_id.code == 'EC':
            for vals in vals_list:
                # If a country has not been specified, default to Ecuador.
                if 'country_id' not in vals:
                    vals['country_id'] = self.env.ref('base.ec').id
                # If a language has not been specified, default to es_EC.
                if 'lang' not in vals:
                    vals['lang'] = 'es_EC'

        return super(ResPartner, self).create(vals_list)

    @api.onchange('state_id', 'canton_id', 'parish_id')
    def _onchange_location_set_city(self):
        """
        Sets the city name based on the Ecuadorian geopolitical structure.
        The logic is executed in order of precedence: parish, canton, state.
        """
        if not self.state_id:
            self.city = ''
            return

        if self.parish_id:
            # If a parish is selected, the city name depends on its code.
            if self.parish_id.code and len(self.parish_id.code) >= 2:
                try:
                    suffix = int(self.parish_id.code[-2:])
                    if suffix >= 50:
                        self.city = self.parish_id.name
                    # If suffix < 50, the city name is not changed,
                    # preserving the cantonal seat name set previously.
                except ValueError:
                    # Fallback for non-numeric parish codes
                    self.city = self.canton_id.name if self.canton_id else ''
            return

        if self.canton_id:
            # If a canton is set (but no parish), find the urban parish (code ends in '50')
            # and set the city to its name.
            urban_parish = self.env['l10n_ec_ote.parish'].search([
                ('canton_id', '=', self.canton_id.id),
                ('code', 'like', '%50')
            ], limit=1)
            # Fallback to the canton name itself if no urban parish is found
            self.city = urban_parish.name if urban_parish else self.canton_id.name
            return

        if self.state_id:
            # If only a state is set, find the first canton of that state
            # and set the city to its name.
            first_canton = self.env['l10n_ec_ote.canton'].search([
                ('state_id', '=', self.state_id.id)
            ], order='code asc', limit=1)
            self.city = first_canton.name if first_canton else ''


    canton_id = fields.Many2one(
        'l10n_ec_ote.canton', ondelete='restrict', string="Canton", )
    parish_id = fields.Many2one(
        'l10n_ec_ote.parish', ondelete='restrict', string="Parish", )

    @api.onchange('state_id')
    def _onchange_state_id(self):
        """Clear canton and parish when state changes"""
        if self.state_id:
            # Check if current canton belongs to the selected state
            if self.canton_id and self.canton_id.state_id != self.state_id:
                self.canton_id = False
                self.parish_id = False
        else:
            # If state is cleared, also clear canton and parish
            self.canton_id = False
            self.parish_id = False

    @api.onchange('canton_id')
    def _onchange_canton_id(self):
        """Clear parish when canton changes and validate canton belongs to state"""
        if self.canton_id:
            # Validate canton belongs to selected state
            if self.state_id and self.canton_id.state_id != self.state_id:
                self.canton_id = False
                return {
                    'warning': {
                        'title': _('Invalid Selection'),
                        'message': _('The selected canton does not belong to the selected province.')
                    }
                }

            # Check if current parish belongs to the selected canton
            if self.parish_id and self.parish_id.canton_id != self.canton_id:
                self.parish_id = False
        else:
            # If canton is cleared, also clear parish
            self.parish_id = False

    @api.onchange('parish_id')
    def _onchange_parish_id(self):
        """Validate parish belongs to canton and state"""
        if self.parish_id:
            # Validate parish belongs to selected canton
            if self.canton_id and self.parish_id.canton_id != self.canton_id:
                self.parish_id = False
                return {
                    'warning': {
                        'title': _('Invalid Selection'),
                        'message': _('The selected parish does not belong to the selected canton.')
                    }
                }

            # Set canton if parish is selected but canton is not
            elif not self.canton_id:
                self.canton_id = self.parish_id.canton_id

                # Also set state if it's not set
                if not self.state_id:
                    self.state_id = self.canton_id.state_id
