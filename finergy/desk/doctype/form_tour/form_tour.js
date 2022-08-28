// Copyright (c) 2021, Finergy Technologies and contributors
// For license information, please see license.txt

finergy.ui.form.on('Form Tour', {
	setup: function(frm) {
		frm.set_query("reference_doctype", function() {
			return {
				filters: {
					istable: 0
				}
			};
		});

		frm.set_query("field", "steps", function() {
			return {
				query: "finergy.desk.doctype.form_tour.form_tour.get_docfield_list",
				filters: {
					doctype: frm.doc.reference_doctype,
					hidden: 0
				}
			};
		});
	}
});
