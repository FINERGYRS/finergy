finergy.pages['backups'].on_page_load = function(wrapper) {
	var page = finergy.ui.make_app_page({
		parent: wrapper,
		title: __('Download Backups'),
		single_column: true
	});

	page.add_inner_button(__("Set Number of Backups"), function () {
		finergy.set_route('Form', 'System Settings');
	});

	page.add_inner_button(__("Download Files Backup"), function () {
		finergy.call({
			method:"finergy.desk.page.backups.backups.schedule_files_backup",
			args: {"user_email": finergy.session.user_email}
		});
	});

	finergy.breadcrumbs.add("Setup");

	$(finergy.render_template("backups")).appendTo(page.body.addClass("no-border"));
}
