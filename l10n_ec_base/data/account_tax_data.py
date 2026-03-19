# data to update into taxes
# return dict(tax_idxml: dict(values to write into tax))
TAX_DATA_EC = {
    "tax_vat_411_goods": {"l10n_ec_xml_fe_code": "2"},
    "tax_vat_411_services": {"l10n_ec_xml_fe_code": "2"},
    "tax_vat_412": {"l10n_ec_xml_fe_code": "2"},
    "tax_vat_413": {"l10n_ec_xml_fe_code": "0"},
    "tax_vat_414": {"l10n_ec_xml_fe_code": "0"},
    "tax_vat_415_goods": {"l10n_ec_xml_fe_code": "0"},
    "tax_vat_415_services": {"l10n_ec_xml_fe_code": "0"},
    "tax_vat_416": {"l10n_ec_xml_fe_code": "0"},
    "tax_vat_417": {"l10n_ec_xml_fe_code": "0"},
    "tax_vat_418": {"l10n_ec_xml_fe_code": "0"},
    "tax_vat_441": {"l10n_ec_xml_fe_code": "7"},
    "tax_vat_444": {"l10n_ec_xml_fe_code": "2"},
    "tax_vat_444_zero_vat": {"l10n_ec_xml_fe_code": "0"},
    "tax_vat_444_not_charged_vat": {"l10n_ec_xml_fe_code": "6"},
    "tax_vat_444_not_exempt_vat": {"l10n_ec_xml_fe_code": "7"},
    "tax_vat_510_sup_01": {"l10n_ec_xml_fe_code": "2"},
    "tax_vat_510_sup_05": {"l10n_ec_xml_fe_code": "2"},
    "tax_vat_510_sup_06": {"l10n_ec_xml_fe_code": "2"},
    "tax_vat_510_sup_15": {"l10n_ec_xml_fe_code": "2"},
    "tax_vat_511_sup_03": {"l10n_ec_xml_fe_code": "2"},
    "tax_vat_512_sup_04": {"l10n_ec_xml_fe_code": "2"},
    "tax_vat_512_sup_05": {"l10n_ec_xml_fe_code": "2"},
    "tax_vat_512_sup_07": {"l10n_ec_xml_fe_code": "2"},
    "tax_vat_513_sup_01": {"l10n_ec_xml_fe_code": "2"},
    "tax_vat_514_sup_06": {"l10n_ec_xml_fe_code": "2"},
    "tax_vat_515_sup_03": {"l10n_ec_xml_fe_code": "2"},
    "tax_vat_516_sup_07": {"l10n_ec_xml_fe_code": "0"},
    "tax_vat_517_sup_02": {"l10n_ec_xml_fe_code": "0"},
    "tax_vat_517_sup_04": {"l10n_ec_xml_fe_code": "0"},
    "tax_vat_517_sup_05": {"l10n_ec_xml_fe_code": "0"},
    "tax_vat_517_sup_07": {"l10n_ec_xml_fe_code": "0"},
    "tax_vat_517_sup_15": {"l10n_ec_xml_fe_code": "0"},
    "tax_vat_518_sup_02": {"l10n_ec_xml_fe_code": "0"},
    "tax_vat_541_sup_02": {"l10n_ec_xml_fe_code": "6"},
    "tax_vat_510_08_sup_01": {"l10n_ec_xml_fe_code": "8"},
    "tax_vat_542_sup_02": {"l10n_ec_xml_fe_code": "7"},
    "tax_vat_545_sup_08": {"l10n_ec_xml_fe_code": "2"},
    "tax_vat_545_sup_08_vat0": {"l10n_ec_xml_fe_code": "0"},
    "tax_vat_545_sup_08_vat_exempt": {"l10n_ec_xml_fe_code": "7"},
    "tax_vat_545_sup_08_vat_not_charged": {"l10n_ec_xml_fe_code": "6"},
    "tax_vat_545_sup_09": {"l10n_ec_xml_fe_code": "2"},
    "tax_withhold_vat_10": {"l10n_ec_xml_fe_code": "9"},
    "tax_withhold_vat_20": {"l10n_ec_xml_fe_code": "10"},
    "tax_withhold_vat_30": {"l10n_ec_xml_fe_code": "1"},
    "tax_withhold_vat_50": {"l10n_ec_xml_fe_code": "11"},
    "tax_withhold_vat_70": {"l10n_ec_xml_fe_code": "2"},
    "tax_withhold_vat_100": {"l10n_ec_xml_fe_code": "3"},
    "tax_sale_withhold_vat_10": {"l10n_ec_xml_fe_code": "9"},
    "tax_sale_withhold_vat_20": {"l10n_ec_xml_fe_code": "10"},
    "tax_sale_withhold_vat_30": {"l10n_ec_xml_fe_code": "1"},
    "tax_sale_withhold_vat_50": {"l10n_ec_xml_fe_code": "11"},
    "tax_sale_withhold_vat_70": {"l10n_ec_xml_fe_code": "2"},
    "tax_sale_withhold_vat_100": {"l10n_ec_xml_fe_code": "3"},
    # SRI Resolution NAC-DGERCGC26-00000009, effective 2026-03-01.
    "tax_withhold_profit_303": {"amount": -10, "active": True},
    "tax_withhold_profit_303A": {
        "amount": -5,
        "active": True,
        "name": "303A 5% Servicios Profesionales Prestados por Sociedades Residentes",
        "description": "303A 5% Professional Services Provided by Resident Companies",
        "invoice_label": "3% 303a",
    },
    "tax_withhold_profit_304": {
        "amount": -10,
        "active": True,
        "name": "10% 304",
        "description": (
            "304 10% Services Predominantly Intellectual Services "
            "not Related to Professional Degree"
        ),
        "invoice_label": "10% 304",
    },
    "tax_withhold_profit_304A": {
        "amount": -10,
        "active": True,
        "name": "10% 304a",
        "description": (
            "304a 10% Commissions and Other Payments for Services "
            "Predominantly Intellectually Unrelated to Professional Title"
        ),
        "invoice_label": "10% 304a",
    },
    "tax_withhold_profit_304B": {
        "amount": -10,
        "active": True,
        "name": "10% 304b",
        "description": (
            "304b 10% Payments to Notaries and Property and Commercial "
            "Registrars for their Activities as Such"
        ),
        "invoice_label": "10% 304b",
    },
    "tax_withhold_profit_304C": {"amount": -10, "active": True},
    "tax_withhold_profit_304D": {"amount": -10, "active": True},
    "tax_withhold_profit_307": {
        "amount": -3,
        "active": True,
        "name": "307 3% Servicios Mano de Obra",
        "description": "307 3% Services Predominantly Labor Force",
        "invoice_label": "2% 307",
    },
    "tax_withhold_profit_308": {"amount": -10, "active": True},
    "tax_withhold_profit_309": {
        "amount": -3,
        "active": True,
        "name": (
            "309 3% Servicios Prestados por Medios de Comunicación y Agencias "
            "de Publicidad"
        ),
        "description": "309 3% Services Rendered by Media and Advertising Agencies",
        "invoice_label": "2.75% 309",
    },
    "tax_withhold_profit_310": {"amount": -1, "active": True},
    "tax_withhold_profit_311": {
        "amount": -3,
        "active": True,
        "name": "311 3% Compra",
        "description": (
            "311 3% For Payments Through Purchase Settlement "
            "(Cultural or Rustic Level)"
        ),
        "invoice_label": "2% 311",
    },
    "tax_withhold_profit_312": {
        "amount": -2,
        "active": True,
        "name": "312 2% Transferencia Bienes",
        "description": (
            "312 2% Transfer of Tangible Movable Property of a Tangible Nature"
        ),
        "invoice_label": "1.75% 312",
    },
    "tax_withhold_profit_312A": {"amount": -1, "active": True},
    "tax_withhold_profit_312C": {"amount": -1.75, "active": True},
    "tax_withhold_profit_314A": {
        "amount": -10,
        "active": True,
        "name": "10% 314a",
        "description": (
            "314a 10% Royalties From Franchises Under The Intellectual "
            "Property Law - Payment to Individuals"
        ),
        "invoice_label": "10% 314a",
    },
    "tax_withhold_profit_314B": {
        "amount": -10,
        "active": True,
        "name": "10% 314b",
        "description": (
            "314b 10% Royalties, Copyrights, Trademarks, Patents and Similar "
            "in Accordance with the Intellectual Property Law - Payment to "
            "Natural Persons"
        ),
        "invoice_label": "10% 314b",
    },
    "tax_withhold_profit_314C": {
        "amount": -10,
        "active": True,
        "name": "10% 314c",
        "description": (
            "314c 10% Royalties from Franchises in Accordance with "
            "Intellectual Property Law - Payment to Corporations"
        ),
        "invoice_label": "10% 314c",
    },
    "tax_withhold_profit_314D": {
        "amount": -10,
        "active": True,
        "name": "10% 314d",
        "description": (
            "314d 10% Royalties, Copyrights, Trademarks, Patents and Similar "
            "Under Intellectual Property law - Payment to Companies"
        ),
        "invoice_label": "10% 314d",
    },
    "tax_withhold_profit_319": {"amount": -2, "active": True},
    "tax_withhold_profit_320": {
        "amount": -10,
        "active": True,
        "name": "10% 320",
        "description": "320 10% For Lease of Real Estate",
        "invoice_label": "10% 320",
    },
    "tax_withhold_profit_322": {
        "amount": -2,
        "active": True,
        "name": "322 2% Seguros y Reaseguros (Primas y Cesiones)",
        "description": "322 2% Insurance and Reinsurance (Premiums and Cessions)",
        "invoice_label": "1% 322",
    },
    # Confirmed codes missing from the upstream 18.0 core template.
    "tax_withhold_profit_323O": {
        "amount": 0,
        "active": True,
        "name": "323O 0% Rendimientos Financieros IFIs",
        "description": (
            "323O 0% Intereses y demás rendimientos financieros pagados a bancos "
            "y otras entidades sometidas al control de la Superintendencia de "
            "Bancos y de la Economía Popular y Solidaria"
        ),
        "invoice_label": "323O",
    },
    "tax_withhold_profit_324A": {
        "amount": -2,
        "active": True,
        "name": "324A 2% Intereses entre IFIs",
        "description": (
            "324A 2% Intereses en operaciones de crédito entre instituciones del "
            "sistema financiero y entidades economía popular y solidaria"
        ),
        "invoice_label": "324A",
    },
    "tax_withhold_profit_324B": {
        "amount": -2,
        "active": True,
        "name": "324B 2% Inversiones entre IFIs",
        "description": (
            "324B 2% Inversiones entre instituciones del sistema financiero y "
            "entidades economía popular y solidaria"
        ),
        "invoice_label": "324B",
    },
    "tax_withhold_profit_324C": {
        "amount": -2,
        "active": True,
        "name": "324C 2% BCE entre IFIs",
        "description": (
            "324C 2% Pagos y créditos en cuenta efectuados por el BCE y los "
            "depósitos centralizados de valores, en calidad de intermediarios, a "
            "instituciones del sistema financiero por cuenta de otras "
            "instituciones del sistema financiero"
        ),
        "invoice_label": "324C",
    },
    "tax_withhold_profit_343": {"amount": -1, "active": True},
    "tax_withhold_profit_343A": {
        "amount": -2,
        "active": True,
        "name": "343A 2% Energia Electrica",
        "description": "343a 2% for electric energy",
        "invoice_label": "1% 343a",
    },
    "tax_withhold_profit_343B": {
        "amount": -2,
        "active": True,
        "name": "343B 2% Construccion",
        "description": "343b 2% For Construction Activities of Real Estate",
        "invoice_label": "1% 343b",
    },
    "tax_withhold_profit_343C": {"amount": -2, "active": True},
    "tax_withhold_profit_344A": {"amount": -2, "active": True},
    "tax_withhold_profit_344B": {"amount": -2, "active": True},
    "tax_withhold_profit_344C": {"amount": -2, "active": True},
    "tax_withhold_profit_304E_10": {"amount": -10, "active": True},
    "tax_withhold_profit_332E": {
        "amount": 0,
        "active": True,
        "name": "332E 0% Cooperativas Transporte",
        "description": (
            "332E 0% Valores entregados por las cooperativas de transporte a sus "
            "socios"
        ),
        "invoice_label": "332E",
    },
    "tax_withhold_profit_332F": {
        "amount": 0,
        "active": True,
        "name": "332F 0% Compraventa de Divisas",
        "description": (
            "332F 0% Compraventa de divisas distintas al dólar de los Estados "
            "Unidos de América"
        ),
        "invoice_label": "332F",
    },
    "tax_withhold_profit_332H": {
        "amount": 0,
        "active": True,
        "name": "332H 0% Tarjeta Exterior",
        "description": (
            "332H 0% Pago al exterior tarjeta de crédito reportada por la "
            "Emisora de tarjeta de crédito, solo recap"
        ),
        "invoice_label": "332H",
    },
    "tax_withhold_profit_3480": {
        "amount": -15,
        "active": True,
        "name": "3480 15% Operadores Pronósticos Deportivos",
        "description": (
            "3480 15% Impuesto a la renta único sobre los ingresos percibidos "
            "por los operadores de pronósticos deportivos"
        ),
        "invoice_label": "3480",
    },
    "tax_withhold_profit_3482": {
        "amount": -5,
        "active": True,
        "name": (
            "3482 5% Comisiones a sociedades, nacionales o extranjeras "
            "residentes y establecimientos permanentes domiciliados en el país"
        ),
        "description": (
            "3482 5% Comisiones a sociedades, nacionales o extranjeras "
            "residentes y establecimientos permanentes domiciliados en el país"
        ),
        "invoice_label": "3% 3482",
    },
    "tax_withhold_profit_304A_10": {"active": False},
    "tax_withhold_profit_304B_10": {"active": False},
    "tax_withhold_profit_309_2_75": {"active": False},
    "tax_withhold_profit_322_1": {"active": False},
    "tax_withhold_profit_3440": {"active": False},
    "tax_withhold_profit_sale_2_75x100": {"active": False},
    # new taxes 2024
    "tax_vat_15_411_goods": {"l10n_ec_xml_fe_code": "4"},
    "tax_vat_15_411_services": {"l10n_ec_xml_fe_code": "4"},
    "tax_vat_15_412": {"l10n_ec_xml_fe_code": "4"},
    "tax_vat_15_444": {"l10n_ec_xml_fe_code": "4"},
    "tax_vat_15_510_sup_01": {"l10n_ec_xml_fe_code": "4"},
    "tax_vat_15_510_sup_05": {"l10n_ec_xml_fe_code": "4"},
    "tax_vat_15_510_sup_06": {"l10n_ec_xml_fe_code": "4"},
    "tax_vat_15_510_sup_15": {"l10n_ec_xml_fe_code": "4"},
    "tax_vat_15_511_sup_03": {"l10n_ec_xml_fe_code": "4"},
    "tax_vat_15_512_sup_04": {"l10n_ec_xml_fe_code": "4"},
    "tax_vat_15_512_sup_05": {"l10n_ec_xml_fe_code": "4"},
    "tax_vat_15_512_sup_07": {"l10n_ec_xml_fe_code": "4"},
    "tax_vat_15_513_sup_01": {"l10n_ec_xml_fe_code": "4"},
    "tax_vat_15_514_sup_06": {"l10n_ec_xml_fe_code": "4"},
    "tax_vat_15_515_sup_03": {"l10n_ec_xml_fe_code": "4"},
    "tax_vat_15_545_sup_08": {"l10n_ec_xml_fe_code": "4"},
    "tax_vat_15_545_sup_09": {"l10n_ec_xml_fe_code": "4"},
    "tax_vat_05_411_goods": {"l10n_ec_xml_fe_code": "5"},
    "tax_vat_05_411_services": {"l10n_ec_xml_fe_code": "5"},
    "tax_vat_05_412": {"l10n_ec_xml_fe_code": "5"},
    "tax_vat_05_444": {"l10n_ec_xml_fe_code": "5"},
    "tax_vat_05_510_sup_01": {"l10n_ec_xml_fe_code": "5"},
    "tax_vat_05_510_sup_05": {"l10n_ec_xml_fe_code": "5"},
    "tax_vat_05_510_sup_06": {"l10n_ec_xml_fe_code": "5"},
    "tax_vat_05_510_sup_15": {"l10n_ec_xml_fe_code": "5"},
    "tax_vat_05_511_sup_03": {"l10n_ec_xml_fe_code": "5"},
    "tax_vat_05_512_sup_04": {"l10n_ec_xml_fe_code": "5"},
    "tax_vat_05_512_sup_05": {"l10n_ec_xml_fe_code": "5"},
    "tax_vat_05_512_sup_07": {"l10n_ec_xml_fe_code": "5"},
    "tax_vat_05_513_sup_01": {"l10n_ec_xml_fe_code": "5"},
    "tax_vat_05_514_sup_06": {"l10n_ec_xml_fe_code": "5"},
    "tax_vat_05_515_sup_03": {"l10n_ec_xml_fe_code": "5"},
    "tax_vat_05_545_sup_08": {"l10n_ec_xml_fe_code": "5"},
    "tax_vat_05_545_sup_09": {"l10n_ec_xml_fe_code": "5"},
}
