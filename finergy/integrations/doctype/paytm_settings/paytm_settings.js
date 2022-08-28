// Copyright (c) 2020, Finergy Technologies and contributors
// For license information, please see license.txt

finergy.ui.form.on('Paytm Settings', {
	refresh: function(frm) {
		frm.dashboard.set_headline(__("For more information, {0}.", [`<a href='https://capkpi.com/docs/user/manual/en/capkpi_integration/paytm-integration'>${__('Click here')}</a>`]));
	}
});
