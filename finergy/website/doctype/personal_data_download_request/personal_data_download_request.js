// Copyright (c) 2019, Finergy Technologies and contributors
// For license information, please see license.txt

finergy.ui.form.on('Personal Data Download Request', {
	onload: function(frm) {
		if (frm.is_new()) {
			frm.doc.user = finergy.session.user;
		}
	},
});
