// Copyright (c) 2016, Finergy Technologies and contributors
// For license information, please see license.txt

finergy.ui.form.on("Address", {
	refresh: function(frm) {
		if(frm.doc.__islocal) {
			const last_doc = finergy.contacts.get_last_doc(frm);
			if(finergy.dynamic_link && finergy.dynamic_link.doc
					&& finergy.dynamic_link.doc.name == last_doc.docname) {
				frm.set_value('links', '');
				frm.add_child('links', {
					link_doctype: finergy.dynamic_link.doctype,
					link_name: finergy.dynamic_link.doc[finergy.dynamic_link.fieldname]
				});
			}
		}
		frm.set_query('link_doctype', "links", function() {
			return {
				query: "finergy.contacts.address_and_contact.filter_dynamic_link_doctypes",
				filters: {
					fieldtype: "HTML",
					fieldname: "address_html",
				}
			}
		});
		frm.refresh_field("links");

		if (frm.doc.links) {
			for (let i in frm.doc.links) {
				let link = frm.doc.links[i];
				frm.add_custom_button(__("{0}: {1}", [__(link.link_doctype), __(link.link_name)]), function() {
					finergy.set_route("Form", link.link_doctype, link.link_name);
				}, __("Links"));
			}
		}
	},
	validate: function(frm) {
		// clear linked customer / supplier / sales partner on saving...
		if(frm.doc.links) {
			frm.doc.links.forEach(function(d) {
				finergy.model.remove_from_locals(d.link_doctype, d.link_name);
			});
		}
	},
	after_save: function(frm) {
		finergy.run_serially([
			() => finergy.timeout(1),
			() => {
				const last_doc = finergy.contacts.get_last_doc(frm);
				if (finergy.dynamic_link && finergy.dynamic_link.doc && finergy.dynamic_link.doc.name == last_doc.docname) {
					for (let i in frm.doc.links) {
						let link = frm.doc.links[i];
						if (last_doc.doctype == link.link_doctype && last_doc.docname == link.link_name) {
							finergy.set_route('Form', last_doc.doctype, last_doc.docname);
						}
					}
				}
			}
		]);
	}
});
