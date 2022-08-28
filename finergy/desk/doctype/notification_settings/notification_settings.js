// Copyright (c) 2019, Finergy Technologies and contributors
// For license information, please see license.txt

finergy.ui.form.on('Notification Settings', {
	onload: (frm) => {
		finergy.breadcrumbs.add({
			label: __('Settings'),
			route: '#modules/Settings',
			type: 'Custom'
		});
		frm.set_query('subscribed_documents', () => {
			return {
				filters: {
					istable: 0
				}
			};
		});
	},

	refresh: (frm) => {
		if (finergy.user.has_role('System Manager')) {
			frm.add_custom_button(__('Go to Notification Settings List'), () => {
				finergy.set_route('List', 'Notification Settings');
			});
		}
	}

});
