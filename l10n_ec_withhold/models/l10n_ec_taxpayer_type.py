from odoo import fields, models


class L10nEcTaxpayerType(models.Model):
    _name = "l10n_ec.taxpayer.type"
    _description = "Taxpayer Type"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, translate=True)
    profit_withhold_tax_id = fields.Many2one(
        comodel_name="account.tax",
        string="Profit Withhold",
        company_dependent=True,
        domain=[("tax_group_id.l10n_ec_type", "=", "withhold_income_purchase")],
        help="Suggested purchase income withhold for vendors in this SRI type.",
    )
    vat_goods_withhold_tax_id = fields.Many2one(
        comodel_name="account.tax",
        string="Goods VAT Withhold",
        company_dependent=True,
        domain=[("tax_group_id.l10n_ec_type", "=", "withhold_vat_purchase")],
        help="Suggested purchase VAT withhold for stockable or consumable products.",
    )
    vat_services_withhold_tax_id = fields.Many2one(
        comodel_name="account.tax",
        string="Services VAT Withhold",
        company_dependent=True,
        domain=[("tax_group_id.l10n_ec_type", "=", "withhold_vat_purchase")],
        help="Suggested purchase VAT withhold for service products.",
    )
    active = fields.Boolean(default=True)
