// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("IJR Picture", {
	refresh(frm) {
        if (frm.doc.image) {
            frm.get_field('image_preview').$wrapper.empty().append(
                $(`<img src="${frm.doc.image}" style="max-width: 100%;">`)
            );
        } else {
            frm.get_field('image_preview').$wrapper.empty().append(
                $(`<p>No Image</p>`)
            );
        }
	},
});
