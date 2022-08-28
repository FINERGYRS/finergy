// Copyright (c) 2019, Finergy Technologies and contributors
// For license information, please see license.txt

finergy.ui.form.on('Event Sync Log', {
	refresh: function(frm) {
		if (frm.doc.status == 'Failed') {
			frm.add_custom_button(__('Resync'), function() {
				finergy.call({
					method: "finergy.event_streaming.doctype.event_producer.event_producer.resync",
					args: {
						update: frm.doc,
					},
					callback: function(r) {
						if (r.message) {
							finergy.msgprint(r.message);
							frm.set_value('status', r.message);
							frm.save();
						}
					}
				});
			});
		}
	}
});
