// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// MIT License. See license.txt
finergy.provide("finergy.desk");

finergy.ui.form.on("Event", {
	onload: function(frm) {
		frm.set_query('reference_doctype', "event_participants", function() {
			return {
				"filters": {
					"issingle": 0,
				}
			};
		});
		frm.set_query('google_calendar', function() {
			return {
				filters: {
					"owner": finergy.session.user
				}
			};
		});
	},
	refresh: function(frm) {
		if(frm.doc.event_participants) {
			frm.doc.event_participants.forEach(value => {
				frm.add_custom_button(__(value.reference_docname), function() {
					finergy.set_route("Form", value.reference_doctype, value.reference_docname);
				}, __("Participants"));
			})
		}

		frm.page.set_inner_btn_group_as_primary(__("Add Participants"));

		frm.add_custom_button(__('Add Contacts'), function() {
			new finergy.desk.eventParticipants(frm, "Contact");
		}, __("Add Participants"));
	},
	repeat_on: function(frm) {
		if(frm.doc.repeat_on==="Every Day") {
			["monday", "tuesday", "wednesday", "thursday",
				"friday", "saturday", "sunday"].map(function(v) {
					frm.set_value(v, 1);
				});
		}
	}
});

finergy.ui.form.on("Event Participants", {
	event_participants_remove: function(frm, cdt, cdn) {
		if (cdt&&!cdn.includes("New Event Participants")){
			finergy.call({
				type: "POST",
				method: "finergy.desk.doctype.event.event.delete_communication",
				args: {
					"event": frm.doc,
					"reference_doctype": cdt,
					"reference_docname": cdn
				},
				freeze: true,
				callback: function(r) {
					if(r.exc) {
						finergy.show_alert({
							message: __("{0}", [r.exc]),
							indicator: 'orange'
						});
					}
				}
			});
		}
	}
});

finergy.desk.eventParticipants = class eventParticipants {
	constructor(frm, doctype) {
		this.frm = frm;
		this.doctype = doctype;
		this.make();
	}

	make() {
		let me = this;

		let table = me.frm.get_field("event_participants").grid;
		new finergy.ui.form.LinkSelector({
			doctype: me.doctype,
			dynamic_link_field: "reference_doctype",
			dynamic_link_reference: me.doctype,
			fieldname: "reference_docname",
			target: table,
			txt: ""
		});
	}
};
