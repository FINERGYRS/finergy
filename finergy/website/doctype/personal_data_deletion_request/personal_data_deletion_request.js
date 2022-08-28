// Copyright (c) 2019, Finergy Technologies and contributors
// For license information, please see license.txt

finergy.ui.form.on("Personal Data Deletion Request", {
	refresh: function(frm) {
		if (
			finergy.user.has_role("System Manager") &&
			frm.doc.status == "Pending Approval"
		) {
			frm.add_custom_button(__("Delete Data"), function() {
				return finergy.call({
					doc: frm.doc,
					method: "trigger_data_deletion",
					freeze: true,
					callback: function() {
						frm.refresh();
					}
				});
			});
		}
	}
});
