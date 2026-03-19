## Known Issues / Limitations

### EDI withholding XML: hardcoded fields in `docsSustento`

The following fields in the SRI withholding XML (`_l10n_ec_get_support_data`) are
currently hardcoded with default values and are not yet configurable:

| Field | Current value | Description |
|---|---|---|
| `pagoLocExt` | `"01"` | Local/foreign payment (01 = local) |
| `tipoRegi` | `False` | Tax regime type (applies to foreign payments) |
| `paisEfecPago` | `False` | Country of effective payment |
| `DobTrib` | `"NO"` | Double taxation agreement |
| `SujRetNorLeg` | `False` | Subject to retention by legal norm |
| `pagoRegFis` | `False` | Payment to tax haven |

These fields are only mandatory in the SRI schema when the payment is foreign
(`pagoLocExt = "02"`). For local payments (the most common case in Ecuador)
the hardcoded defaults produce a valid XML.

Support for foreign payment scenarios is planned for a future iteration.

### EDI withholding XML: `tipoSujetoRetenido` for foreign companies

When the withheld subject has a foreign identification (`type_id == "08"`),
the field `tipoSujetoRetenido` is always sent as `"01"` (Natural Person).
Determining whether a foreign subject is a natural person (`"01"`) or a
company (`"02"`) is not yet implemented.
