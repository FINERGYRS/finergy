// Copyright (c) 2020, Finergy Technologies and contributors
// For license information, please see license.txt

finergy.ui.form.on('Module Profile', {
	refresh: function(frm) {
		if (has_common(finergy.user_roles, ["Administrator", "System Manager"])) {
			if (!frm.module_editor && frm.doc.__onload && frm.doc.__onload.all_modules) {
				let module_area = $('<div style="min-height: 300px">')
					.appendTo(frm.fields_dict.module_html.wrapper);

				frm.module_editor = new finergy.ModuleEditor(frm, module_area);
			}
		}

		if (frm.module_editor) {
			frm.module_editor.refresh();
		}
	}
});
