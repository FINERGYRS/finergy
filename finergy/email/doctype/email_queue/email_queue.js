// Copyright (c) 2016, Finergy Technologies and contributors
// For license information, please see license.txt

finergy.ui.form.on("Email Queue", {
	refresh: function(frm) {
		if (["Not Sent","Partially Sent"].indexOf(frm.doc.status)!=-1) {
			let button = frm.add_custom_button("Send Now", function() {
				finergy.call({
					method: 'finergy.email.doctype.email_queue.email_queue.send_now',
					args: {
						name: frm.doc.name
					},
					btn: button,
					callback: function() {
						frm.reload_doc();
					}
				});
			});
		}

		if (["Error","Partially Errored"].indexOf(frm.doc.status)!=-1) {
			let button = frm.add_custom_button("Retry Sending", function() {
				frm.call({
					method: "retry_sending",
					args: {
						name: frm.doc.name
					},
					btn: button,
					callback: function(r) {
						if (!r.exc) {
							frm.set_value("status", "Not Sent");
						}
					}
				})
			});
		}
	}
});
