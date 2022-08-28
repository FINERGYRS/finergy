// Copyright (c) 2017, Finergy Technologies and contributors
// For license information, please see license.txt

finergy.ui.form.on('Data Migration Plan', {
	onload(frm) {
		frm.add_custom_button(__('Run'), () => finergy.new_doc('Data Migration Run', {
			data_migration_plan: frm.doc.name
		}));
	}
});
