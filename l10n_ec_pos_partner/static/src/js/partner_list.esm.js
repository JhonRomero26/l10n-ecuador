/** @odoo-module */ // eslint-disable-line jsdoc/check-tag-names

import {PartnerList} from "@point_of_sale/app/screens/partner_list/partner_list";
import {AlertDialog} from "@web/core/confirmation_dialog/confirmation_dialog";
import {_t} from "@web/core/l10n/translation";
import {patch} from "@web/core/utils/patch";

patch(PartnerList.prototype, {
    async editPartner(p = false) {
        const query = this.state.query;
        const is_ci_ruc =
            query &&
            (query.length === 10 || query.length === 13) &&
            /^[0-9]+$/.test(query);

        if (!p && is_ci_ruc) {
            try {
                const partner_data = [
                    {
                        name: query,
                    },
                ];

                const partnerId = await this.env.services.orm.call(
                    "res.partner",
                    "create_from_ui",
                    [partner_data]
                );

                await this.pos.data.read("res.partner", [partnerId]);
                const newPartner = this.pos.models["res.partner"].get(partnerId);

                if (newPartner) {
                    const editedPartner = await this.pos.editPartner(newPartner);
                    if (editedPartner) {
                        this.props.getPayload(editedPartner);
                        this.props.close();
                    } else {
                        this.props.close();
                    }
                } else {
                    return super.editPartner.apply(this, arguments);
                }
            } catch (error) {
                const message =
                    error.message?.data?.message || _t("Could not create customer.");
                this.dialog.add(AlertDialog, {
                    title: _t("Error"),
                    body: message,
                });
            }
        } else {
            return super.editPartner.apply(this, arguments);
        }
    },
});
