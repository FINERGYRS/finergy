// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// MIT License. See license.txt

finergy.ui.form.on('Role', {
	refresh: function(frm) {
		frm.set_df_property('is_custom', 'read_only', finergy.session.user !== 'Administrator');

		frm.add_custom_button("Role Permissions Manager", function() {
			finergy.route_options = {"role": frm.doc.name};
			finergy.set_route("permission-manager");
		});
		frm.add_custom_button("Show Users", function() {
			finergy.route_options = {"role": frm.doc.name};
			finergy.set_route("List", "User", "Report");
		});
	}
});
