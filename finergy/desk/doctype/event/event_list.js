finergy.listview_settings['Event'] = {
	add_fields: ["starts_on", "ends_on"],
	onload: function() {
		finergy.route_options = {
			"status": "Open"
		};
	}
}