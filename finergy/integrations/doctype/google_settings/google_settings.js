// Copyright (c) 2019, Finergy Technologies and contributors
// For license information, please see license.txt

finergy.ui.form.on('Google Settings', {
	refresh: function(frm) {
		frm.dashboard.set_headline(__("For more information, {0}.", [`<a href='https://capkpi.com/docs/user/manual/en/capkpi_integration/google_settings'>${__('Click here')}</a>`]));
	}
});
