// Copyright (c) 2016, Finergy Technologies and contributors
// For license information, please see license.txt

finergy.ui.form.on('Page', {
	refresh: function(frm) {
		if (!finergy.boot.developer_mode && finergy.session.user != 'Administrator') {
			// make the document read-only
			frm.set_read_only();
		}
		if (!frm.is_new() && !frm.doc.istable) {
			frm.add_custom_button(__('Go to {0} Page', [frm.doc.title || frm.doc.name]), () => {
				finergy.set_route(frm.doc.name);
			});
		}
	}
});
