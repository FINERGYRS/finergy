// Copyright (c) 2017, Finergy Technologies and contributors
// For license information, please see license.txt

finergy.ui.form.on('Print Style', {
	refresh: function(frm) {
		frm.add_custom_button(__('Print Settings'), () => {
			finergy.set_route('Form', 'Print Settings');
		})
	}
});
